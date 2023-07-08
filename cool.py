import os
from bs4 import BeautifulSoup


def main(directory):
    # Get the list of HTML files.
    html_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith((".html", ".htm")):
                html_files.append(os.path.join(root, file))

    # Loop through the HTML files.
    for html_file_name in html_files:
        # Open the HTML file with the correct encoding.
        with open(html_file_name, "r", encoding="utf-8") as html_file_obj:
            # Parse the HTML content.
            soup = BeautifulSoup(html_file_obj, "html.parser")

        # Find all elements with inline styles.
        elements_with_styles = soup.find_all(style=True)

        if elements_with_styles:
            # Create a new CSS file.
            css_file_name = os.path.splitext(html_file_name)[0] + ".css"
            with open(css_file_name, "w") as css_file:
                # Write the CSS selectors and styles to the CSS file.
                css_file.write("/* Generated CSS from inline styles */\n")

                written_selectors = set()
                temp_id_counter = 1

                for element in elements_with_styles:
                    selector, is_temp_id = get_css_selector(element, temp_id_counter)
                    if selector not in written_selectors:
                        styles = element["style"].split(";")
                        declarations = []
                        for style in styles:
                            property_value = style.strip()
                            if property_value:
                                declarations.append(f"{property_value};")
                        css_file.write(
                            f"{selector} {{\n    "
                            + "\n    ".join(declarations)
                            + "\n}\n"
                        )
                        written_selectors.add(selector)

                        if is_temp_id:
                            # Add the temporary ID to the corresponding HTML element.
                            add_temp_id_to_element(element, temp_id_counter)
                            temp_id_counter += 1
                    else:
                        remove_temp_id_from_element(element)

                print(f"Created CSS file: {css_file_name}")

            # Remove inline styles from HTML elements.
            for element in elements_with_styles:
                del element["style"]

            # Create a new <link> tag for the CSS file.
            link_tag = soup.new_tag("link", rel="stylesheet", href=css_file_name)

            # Insert the <link> tag at the beginning of the <head> tag.
            head_tag = soup.find("head")
            if head_tag:
                head_tag.insert(0, link_tag)
            else:
                # If <head> tag is not present, create one and add the <link> tag.
                head_tag = soup.new_tag("head")
                head_tag.insert(0, link_tag)
                soup.insert(0, head_tag)

            # Save the modified HTML file.
            with open(html_file_name, "w", encoding="utf-8") as new_html_file:
                # Convert the BeautifulSoup object to a string.
                html_string = str(soup)

                # Find the position where the <link> tag is inserted.
                link_position = html_string.find(
                    f'<link rel="stylesheet" href="{css_file_name}"/>'
                )

                # Insert a newline character before and after the <link> tag.
                html_string = (
                    html_string[:link_position] + "\n" + html_string[link_position:]
                )

                # Write the modified HTML string to the file.
                new_html_file.write(html_string)

            print(f"Modified HTML file: {html_file_name}")


def get_css_selector(element, temp_id_counter):
    """Generate a CSS selector for the given element starting from the last element with ID or class.
    Returns the selector and a flag indicating whether a temporary ID is used."""
    selectors = []
    element_id = element.get("id")
    if element_id:
        selectors.append(f"#{element_id}")
        return " ".join(selectors), False
    else:
        found_id_or_class = False
        if element and element.name != "html":
            if element.get("class"):
                classes = ".".join(element["class"])
                selector = f"{element.name}.{classes}"
                found_id_or_class = True
            elif not found_id_or_class:
                temp_id = f"temp{temp_id_counter}"
                selector = f"{element.name}#{temp_id}"
                temp_id_counter += 1
            else:
                selector = element.name

            selectors.insert(0, selector)
            element = element.parent

        return " ".join(selectors), True


def add_temp_id_to_element(element, temp_id_counter):
    """Add a temporary ID attribute to the given element."""
    temp_id = f"temp{temp_id_counter}"
    element["id"] = temp_id


def remove_temp_id_from_element(element):
    """Remove the temporary ID attribute from the given element."""
    element_id = element.get("id")
    if element_id and element_id.startswith("temp"):
        del element["id"]


if __name__ == "__main__":
    directory = "."  # Replace with your desired directory
    main(directory)