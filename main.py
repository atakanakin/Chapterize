from service.run import run_pipeline
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Chapterize: Convert YouTube videos to shorts"
    )
    parser.add_argument("--video", required=True, help="YouTube video URL to process")
    args = parser.parse_args()

    run_pipeline(youtube_url=args.video)


if __name__ == "__main__":
    main()
