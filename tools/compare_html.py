import argparse
from bs4 import BeautifulSoup
from difflib import ndiff


def highlight_changes(previous_html, latest_html):
    previous_soup = BeautifulSoup(previous_html, "html.parser")
    latest_soup = BeautifulSoup(latest_html, "html.parser")

    previous_lines = previous_soup.prettify().splitlines()
    latest_lines = latest_soup.prettify().splitlines()

    diff = list(ndiff(previous_lines, latest_lines))

    highlighted_html = []
    for line in diff:
        if line.startswith("- "):
            highlighted_html.append(
                f'<span style="background-color: #f5c6cb; color: black;">{line[2:]}</span>'
            )
        elif line.startswith("+ "):
            highlighted_html.append(
                f'<span style="background-color: #c3e6cb; color: black;">{line[2:]}</span>'
            )
        elif line.startswith("? "):
            continue  # Skip lines that only indicate position of changes
        else:
            highlighted_html.append(line[2:])

    return "\n".join(highlighted_html)


def generate_diff_html(previous_file, latest_file, output_file):
    print(f"Opening previous HTML file: {previous_file}")
    with open(previous_file, "r", encoding="utf-8") as file:
        previous_html = file.read()

    print(f"Opening latest HTML file: {latest_file}")
    with open(latest_file, "r", encoding="utf-8") as file:
        latest_html = file.read()

    print("Generating differences between the previous and latest HTML files")
    diff_html = highlight_changes(previous_html, latest_html)

    print(f"Writing the differences to the output file: {output_file}")
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(diff_html)

    print("HTML comparison and highlighting complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Compare two HTML files and highlight differences. "
        "The previous file will be compared with the latest file, "
        "and the differences will be highlighted in the output file."
    )

    parser.add_argument(
        "--previous", required=True, help="Path to the previous HTML file to compare."
    )
    parser.add_argument(
        "--latest",
        required=True,
        help="Path to the latest HTML file to compare with the previous file.",
    )
    parser.add_argument(
        "--output",
        default="diff.html",
        help="Path to the output HTML file (default: diff.html).",
    )

    args = parser.parse_args()

    # Call the function to generate the HTML diff
    generate_diff_html(args.previous, args.latest, args.output)


if __name__ == "__main__":
    main()
