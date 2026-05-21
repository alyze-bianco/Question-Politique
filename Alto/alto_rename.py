import os

import xml.etree.ElementTree as ET

def rename_files_and_update_xml(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            xml_path = os.path.join(directory, filename)
            # Parse the XML file
            tree = ET.parse(xml_path)
            ET.register_namespace('', 'http://www.loc.gov/standards/alto/ns-v4#')
            root = tree.getroot()

            img_extension = None
            #detect image extention
            for file_name_tag in root.findall(".//{http://www.loc.gov/standards/alto/ns-v4#}fileName"):
                imgfilename, file_extension = os.path.splitext(file_name_tag.text)
                if(file_extension not in ['', None]):
                    img_extension = file_extension
                    break
                break

            if img_extension is None:
                print(f"Image extension not found in {filename}")
                continue
            img_path = xml_path.replace(".xml", img_extension)
            

            
            # Extract PHYSICAL_IMG_NR
            physical_img_nr = None
            for page in root.findall(".//{http://www.loc.gov/standards/alto/ns-v4#}Page"):
                physical_img_nr = page.get("PHYSICAL_IMG_NR")
                if physical_img_nr:
                    break
            
            if not physical_img_nr:
                print(f"PHYSICAL_IMG_NR not found in {filename}")
                continue
            offset = 199
            newPageNumber = int(physical_img_nr)+offset
            # Generate new name
            new_name = f"p_{newPageNumber:05d}"
            new_xml_name = f"{new_name}.xml"
            new_img_name = f"{new_name}{img_extension}"
            
            # Update <fileName> in XML
            for file_name_tag in root.findall(".//{http://www.loc.gov/standards/alto/ns-v4#}fileName"):
                file_name_tag.text = new_img_name
                break
            
            # Save updated XML
            tree.write(xml_path,"UTF-8",True)
            
            # Rename files
            os.rename(xml_path, os.path.join(directory, new_xml_name))
            if os.path.exists(img_path):
                os.rename(img_path, os.path.join(directory, new_img_name))
            
            print(f"Renamed {filename} and corresponding JPG to {new_name}")

# Replace 'your_directory_path' with the path to the directory containing your files
rename_files_and_update_xml(r"\\wsl.localhost\Ubuntu\home\aly\GithubLinux\OCR_corpus_principal\Alto_to_rename\export_doc760_le_reveille_matin_part2_alto_20260316073332")