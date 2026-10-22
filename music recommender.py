import csv
import os

FILE_NAME = "songs.csv"


def load_songs():
    """Load song data from the CSV file."""
    if not os.path.exists(FILE_NAME):
        print("Error: songs.csv file not found!")
        return []

    with open(FILE_NAME, "r", encoding="utf-8-sig",
              newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def recommend_by_genre(songs):
    genre = input("Enter your favourite genre: ").strip().lower()

    results = [
        song for song in songs
        if song["Genre"].strip().lower() == genre
    ]

    show_recommendations(results)


def recommend_by_artist(songs):
    artist = input("Enter your favourite artist: ").strip().lower()

    results = [
        song for song in songs
        if artist in song["Artist"].strip().lower()
    ]

    show_recommendations(results)


def recommend_by_song(songs):
    title = input("Enter a song you like: ").strip().lower()

    selected = [
        song for song in songs
        if title in song["Song"].strip().lower()
    ]

    if not selected:
        print("Song not found in the dataset.")
        return

    # Find similar songs by the same genre.
    genres = {song["Genre"].strip().lower()
              for song in selected}

    results = [
        song for song in songs
        if song["Genre"].strip().lower() in genres
        and song not in selected
    ]

    print("\nSongs similar in genre:")
    show_recommendations(results)


def show_recommendations(results):
    if not results:
        print("\nNo matching songs found.")
        print("Try another genre, artist, or song.")
        return

    print("\nRecommended Songs")
    print("-" * 55)

    for number, song in enumerate(results, start=1):
        print(f"{number}. {song['Song']}")
        print(f"   Artist: {song['Artist']}")
        print(f"   Genre: {song['Genre']}")
        print(f"   Language: {song['Language']}")
        print()


def main():
    songs = load_songs()

    if not songs:
        return

    print("=" * 40)
    print("   MUSIC RECOMMENDATION SYSTEM")
    print("=" * 40)

    while True:
        print("\n1. Recommend by genre")
        print("2. Recommend by artist")
        print("3. Recommend by favourite song")
        print("4. Display all songs")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            recommend_by_genre(songs)
        elif choice == "2":
            recommend_by_artist(songs)
        elif choice == "3":
            recommend_by_song(songs)
        elif choice == "4":
            show_recommendations(songs)
        elif choice == "5":
            print("Thank you for using the system!")
            break
        else:
            print("Invalid choice. Please enter 1 to 5.")


if __name__ == "__main__":
    main()
