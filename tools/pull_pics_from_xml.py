import os
import xml.etree.ElementTree as ET
import argparse


# Function to process each XML file and return the result
def process_xml_file(file_path):
    print(f"\nProcessing file: {file_path}")
    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Initialize a list to store results
        results = []

        # Define a helper function to process each item
        def process_item(item):
            item_number_element = item.find("itemNumber")
            support_element = item.find("support")

            if item_number_element is None:
                raise ValueError("Element 'itemNumber' not found")
            item_number = item_number_element.text

            if support_element is None:
                raise ValueError("Element 'support' not found")
            support = support_element.text

            # Convert the support value to 1 or 0
            support_value = 1 if support.lower() in ["true", "1"] else 0

            # Add the result to the list
            results.append(f"{item_number}={support_value}")

        # Process all relevant items in the XML
        pics_items = root.findall(".//picsItem")
        pixit_items = root.findall(".//pixitItem")
        cluster_side_items = root.findall(".//clusterSide//picsItem")

        print(f"  Found {len(pics_items)} picsItem elements.")
        print(f"  Found {len(pixit_items)} pixitItem elements.")
        print(f"  Found {len(cluster_side_items)} clusterSide/picsItem elements.")

        for item in pics_items:
            process_item(item)

        for item in pixit_items:
            process_item(item)

        for item in cluster_side_items:
            process_item(item)

        # Return results as a single string
        result_str = "\n".join(results)
        print(f"  Processed {len(results)} items.")
        return result_str

    except Exception as e:
        print(f"  Error processing file {file_path}: {e}")
        return None


def main(directory):
    print(f"\nStarting processing of directory: {directory}")
    output_file = "PICS_FOR_UI_AUTOMATED_TEST.txt"
    output_file_path = os.path.join(
        directory, output_file
    )  # Full path for the output file
    output_lines = []

    # Check if the directory exists
    if not os.path.isdir(directory):
        print(f"  Directory does not exist: {directory}")
        return

    # Iterate through all XML files in the directory
    xml_files = [f for f in os.listdir(directory) if f.endswith(".xml")]
    print(f"  Found {len(xml_files)} XML files.")

    if not xml_files:
        print("  No XML files found in the directory.")
        return

    for filename in xml_files:
        file_path = os.path.join(directory, filename)
        print(f"\n  Processing file: {filename}")
        result = process_xml_file(file_path)
        if result is not None:
            # Remove .xml extension from filename
            base_filename = os.path.splitext(filename)[0]
            output_lines.append(f"# {base_filename}\n")
            output_lines.append(f"\n{result}\n\n")  # Added an extra newline here

    # Write the output to the file
    if output_lines:
        try:
            with open(output_file_path, "w") as f:
                f.writelines(output_lines)
            print(f"\nOutput written to {output_file_path}")
        except IOError as e:
            print(f"  Error writing to file {output_file_path}: {e}")
    else:
        print("  No results to write.")

    print("Processing finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process XML files in a directory and save output to a text file."
    )
    parser.add_argument(
        "--dir", required=True, help="Directory containing the XML files"
    )
    args = parser.parse_args()

    print("Starting the script...")
    main(args.dir)
    print("Script finished.")
