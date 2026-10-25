import csv
import os
import sys
import time
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class BookInput:
    """Model input pencarian: book_id merupakan kunci unik bertipe string."""
    book_id: str


@dataclass
class BookOutput:
    """Model output ringkas yang ditampilkan ketika buku ditemukan."""
    book_id: str
    title: str
    authors: str
    publisher: str
    published_date: Optional[date]
    categories: str
    language: str


def parse_published_date(value: str) -> Optional[date]:
    """
    Mengubah tanggal berformat YYYY-MM-DD menjadi objek date.
    Data kosong atau yang hanya berisi tahun tidak diubah menjadi tanggal
    buatan; nilainya menjadi None karena bulan dan hari tidak tersedia.
    """
    value = (value or "").strip()
    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def load_books(csv_path: str) -> list[dict]:
    """Membaca dataset CSV dan menyimpan setiap baris sebagai dictionary."""
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def output_book(record: Optional[dict]) -> Optional[BookOutput]:
    """Mengubah satu record CSV menjadi objek BookOutput."""
    if record is None:
        return None

    return BookOutput(
        book_id=str(record.get("book_id", "")),
        title=str(record.get("title", "")),
        authors=str(record.get("authors", "")),
        publisher=str(record.get("publisher", "")),
        published_date=parse_published_date(record.get("published_date", "")),
        categories=str(record.get("categories", "")),
        language=str(record.get("language", "")),
    )


def linear_search(books: list[dict], book_id: str):
    """Mengembalikan (record, jumlah perbandingan) dengan Linear Search."""
    comparisons = 0
    for book in books:
        comparisons += 1
        if str(book.get("book_id", "")) == book_id:
            return book, comparisons
    return None, comparisons


def binary_search(sorted_books: list[dict], book_id: str):
    """Binary Search pada data yang sudah diurutkan berdasarkan book_id."""
    low, high = 0, len(sorted_books) - 1
    comparisons = 0

    while low <= high:
        mid = (low + high) // 2
        mid_id = str(sorted_books[mid].get("book_id", ""))
        comparisons += 1

        if mid_id == book_id:
            return sorted_books[mid], comparisons
        if mid_id < book_id:
            low = mid + 1
        else:
            high = mid - 1

    return None, comparisons


def show_result(
    algorithm: str,
    record: Optional[dict],
    comparisons: int,
    elapsed_ms: float,
) -> None:
    result = output_book(record)
    print(f"\n{algorithm}")

    if result is None:
        print("Data buku tidak ditemukan.")
    else:
        print("Data buku ditemukan:")
        print(f"  book_id       : {result.book_id}")
        print(f"  Judul         : {result.title}")
        print(f"  Penulis       : {result.authors}")
        print(f"  Penerbit      : {result.publisher}")

        if result.published_date is not None:
            tanggal = result.published_date.isoformat()
        else:
            tanggal = "Tidak tersedia atau format tidak lengkap"

        print(f"  Tanggal terbit: {tanggal}")
        print(f"  Kategori      : {result.categories}")
        print(f"  Bahasa        : {result.language}")

    print(f"Jumlah perbandingan: {comparisons}")
    print(f"Waktu eksekusi: {elapsed_ms:.6f} ms")


def timed_search(function, data, key):
    start = time.perf_counter()
    record, comparisons = function(data, key)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return record, comparisons, elapsed_ms


def benchmark(books: list[dict]) -> None:
    print("\n=== Pengujian ukuran input n = 100, 1.000, 10.000 ===")

    for n in (100, 1000, 10000):
        if len(books) < n:
            print(
                f"\nPengujian n={n} dilewati karena dataset hanya memiliki "
                f"{len(books)} baris."
            )
            continue

        data = books[:n]
        sorted_data = sorted(
            data, key=lambda row: str(row.get("book_id", ""))
        )
        scenarios = [
            ("awal", str(data[0].get("book_id", ""))),
            ("tengah", str(data[n // 2].get("book_id", ""))),
            ("akhir", str(data[-1].get("book_id", ""))),
            ("tidak ditemukan", "NOT_A_REAL_BOOK_ID"),
        ]

        print(f"\nUkuran input n={n}")
        print(
            f"{'Algoritma':<16}{'Skenario':<20}"
            f"{'Perbandingan':>14}{'Waktu (ms)':>15}"
        )

        for scenario, key in scenarios:
            for name, function, search_data in (
                ("Linear Search", linear_search, data),
                ("Binary Search", binary_search, sorted_data),
            ):
                _, count, elapsed = timed_search(
                    function, search_data, key
                )
                print(
                    f"{name:<16}{scenario:<20}"
                    f"{count:>14}{elapsed:>15.6f}"
                )


def main():
    # Lokasi folder tempat file Python ini disimpan.
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Jika argumen CSV tidak diberikan, gunakan CSV di folder yang sama.
    if len(sys.argv) > 1:
        csv_argument = sys.argv[1]
        if os.path.isabs(csv_argument):
            csv_path = csv_argument
        else:
            csv_path = os.path.join(base_dir, csv_argument)
    else:
        csv_path = os.path.join(base_dir, "google_books_dataset.csv")

    if not os.path.isfile(csv_path):
        print(f"File dataset tidak ditemukan: {csv_path}")
        print("Pastikan file CSV berada di folder yang benar.")
        return

    books = load_books(csv_path)
    if not books:
        print("Dataset kosong.")
        return

    print(f"Jumlah buku yang dibaca: {len(books)}")
    print("Contoh kunci book_id yang tersedia:", books[0].get("book_id", ""))

    key = input(
        "Masukkan book_id yang ingin dicari "
        "(Enter untuk melewati pencarian): "
    ).strip()

    if key:
        record, count, elapsed = timed_search(linear_search, books, key)
        show_result("Linear Search", record, count, elapsed)

        sorted_books = sorted(
            books, key=lambda row: str(row.get("book_id", ""))
        )
        record, count, elapsed = timed_search(
            binary_search, sorted_books, key
        )
        show_result("Binary Search", record, count, elapsed)

    benchmark(books)


if __name__ == "__main__":
    main()
