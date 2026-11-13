import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent


def muat_json(nama):
    with open(BASE / nama, encoding="utf-8") as f:
        return json.load(f)


def validasi(kb):
    """Pastikan setiap aturan menunjuk sumber yang ada dan '!' hanya untuk fakta dasar."""
    ids = set()
    for a in kb["aturan"]:
        if a["id"] in ids:
            sys.exit(f"ID aturan ganda: {a['id']}")
        ids.add(a["id"])
        if a["mode"] not in ("dan", "atau"):
            sys.exit(f"Mode aturan {a['id']} harus 'dan' atau 'atau'")
        if not a["sumber"] or any(s not in kb["sumber"] for s in a["sumber"]):
            sys.exit(f"Aturan {a['id']} tidak menunjuk sumber yang valid")
        for k in a["jika"]:
            if k.startswith("!") and k[1:] not in kb["fakta"]:
                sys.exit(f"Aturan {a['id']}: '!' hanya boleh untuk fakta dasar ({k})")


def label(kb, fid):
    return kb["fakta"].get(fid) or kb["fakta_turunan"].get(fid, fid)


def kondisi_ok(k, memori):
    return (k[1:] not in memori) if k.startswith("!") else (k in memori)


def syarat_terpenuhi(aturan, memori):
    hasil = [kondisi_ok(k, memori) for k in aturan["jika"]]
    return all(hasil) if aturan["mode"] == "dan" else any(hasil)


def tanya_user(kb, jawaban_ya=None):
    """Kumpulkan fakta dasar. Fakta yang dijawab 'tidak' tidak masuk memori."""
    memori = set()
    print(kb["judul"])
    print("Jawab y/t.")
    for no, (fid, teks) in enumerate(kb["fakta"].items(), 1):
        if jawaban_ya is not None:
            j = "y" if fid in jawaban_ya else "t"
            print(f"{no}. {teks}? (y/t) > {j}")
        else:
            while True:
                j = input(f"{no}. {teks}? (y/t) > ").strip().lower()
                if j in ("y", "t"):
                    break
                print("   Ketik y atau t.")
        if j == "y":
            memori.add(fid)
    return memori


def forward_chaining(kb, memori):
    """Jalankan aturan yang cocok sampai tidak ada aturan baru. Kembalikan {fakta: aturan}."""
    asal = {}
    siklus = 0
    while True:
        cocok = [a for a in kb["aturan"]
                 if syarat_terpenuhi(a, memori) and a["maka"] not in memori]
        if not cocok:
            print(f"Siklus {siklus + 1}: tidak ada aturan baru, berhenti")
            return asal
        r = cocok[0]
        siklus += 1
        memori.add(r["maka"])
        asal[r["maka"]] = r
        print(f"Siklus {siklus}: {r['id']} -> {r['maka']}")


def jelaskan(kb, fakta, asal, memori, tingkat=0):
    r = asal.get(fakta)
    if r is None:
        return
    terpenuhi = []
    for k in r["jika"]:
        if kondisi_ok(k, memori):
            terpenuhi.append("tidak ada: " + label(kb, k[1:]) if k.startswith("!") else label(kb, k))
    pad = "  " * tingkat
    print(f"{pad}{label(kb, fakta)}  <- {r['id']} ({'; '.join(terpenuhi)}) [sumber: {', '.join(r['sumber'])}]")
    for k in r["jika"]:
        if not k.startswith("!") and k in asal:
            jelaskan(kb, k, asal, memori, tingkat + 1)


def jalankan(kb, jawaban_ya=None):
    memori = tanya_user(kb, jawaban_ya)
    print("\nFakta awal:", ", ".join(sorted(memori)) or "(tidak ada)")
    print()
    asal = forward_chaining(kb, memori)
    akhir = [k for k in kb["kesimpulan_akhir"] if k in memori]
    print()
    if akhir:
        for k in akhir:
            print("Kesimpulan:", label(kb, k))
        print("Alasan:")
        for k in akhir:
            jelaskan(kb, k, asal, memori, 1)
    else:
        print("Kesimpulan: tidak ada kesimpulan yang dapat ditarik dari fakta yang diberikan")
        print("Alasan: tidak ada aturan akhir yang syaratnya terpenuhi.")
        if asal:
            print("Fakta turunan yang sempat dicapai:")
            for f in asal:
                print("  -", label(kb, f), f"({asal[f]['id']})")
    print("\nCatatan batas keberlakuan:", kb["batas"])
    return set(akhir)


def main():
    p = argparse.ArgumentParser(description="Sistem pakar kelayakan KIP Kuliah (forward chaining)")
    p.add_argument("--kasus", type=int, help="putar ulang kasus uji dengan nomor ini")
    p.add_argument("--uji", action="store_true", help="jalankan semua kasus uji dan cek hasilnya")
    args = p.parse_args()

    kb = muat_json("kb_beasiswa.json")
    validasi(kb)
    kasus = muat_json("kasus_uji.json")

    if args.uji:
        gagal = 0
        for k in kasus:
            print("=" * 70)
            print(f"KASUS {k['id']}: {k['nama']}")
            hasil = jalankan(kb, set(k["jawaban_ya"]))
            ok = hasil == set(k["harapan"])
            gagal += not ok
            print(f"\n>>> Harapan: {k['harapan'] or 'tidak ada kesimpulan'} | {'LULUS' if ok else 'GAGAL'}")
        print("=" * 70)
        print(f"{len(kasus) - gagal}/{len(kasus)} kasus uji sesuai harapan")
        sys.exit(1 if gagal else 0)
    elif args.kasus:
        pilih = [k for k in kasus if k["id"] == args.kasus]
        if not pilih:
            sys.exit(f"Kasus {args.kasus} tidak ada")
        jalankan(kb, set(pilih[0]["jawaban_ya"]))
    else:
        jalankan(kb)


if __name__ == "__main__":
    main()
