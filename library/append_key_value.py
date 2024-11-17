#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule

def main():
    module_args = dict(
        file_path=dict(type='str', required=True),
        key=dict(type='str', required=True),
        value=dict(type='list', elements='str', required=True),
        delimiter=dict(type='str', required=False, default=","),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    file_path = module.params['file_path']
    key = module.params['key']
    values = module.params['value']
    delimiter = module.params['delimiter']

    debug_logs = []  # Collect debug messages

    try:
        # Debug input parameters
        debug_logs.append(f"Input Parameters - file_path: {file_path}, key: {key}, values: {values}, delimiter: {delimiter}")

        # Read the file if it exists
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
            debug_logs.append(f"File read successfully. Contents: {lines}")
        except FileNotFoundError:
            lines = []
            debug_logs.append("File not found. Starting with empty content.")

        found_key = False
        updated_lines = []

        # Process the file line by line
        for line in lines:
            debug_logs.append(f"Processing line: {line.strip()}")
            # Check if the line starts with 'key=' (key followed by equal sign)
            if line.strip().startswith(f"{key}="):
                found_key = True
                debug_logs.append(f"Found line with key: {line.strip()}")

                # Get the current values after the '=' sign
                current_values = line.strip().split('=', 1)[1].split(delimiter)
                debug_logs.append(f"Current values: {current_values}")

                # Add values only if they are not already present
                for value in values:
                    if value not in current_values:
                        current_values.append(value)
                        debug_logs.append(f"Added value: {value}")
                debug_logs.append(f"Current values after append: {current_values}")
                
                # Removing empty elements
                current_values = [value for value in current_values if value != '']
                debug_logs.append(f"Current values after appending and removing empty elements: {current_values}")

                # Reconstruct the line with updated values
                line = f"{key}={delimiter.join(current_values)}\n"

            debug_logs.append(f"Updated line: {line.strip()}")
            
            updated_lines.append(line)

        # Add the key if not found
        if not found_key:
            debug_logs.append(f"Key '{key}' not found in file. Adding it.")
            updated_lines.append(f"{key}={delimiter.join(values)}\n")

        # Write changes if needed
        if lines != updated_lines:
            debug_logs.append("Changes detected. Writing updated content to the file.")
            if not module.check_mode:
                with open(file_path, 'w') as file:
                    file.writelines(updated_lines)
            module.exit_json(changed=True, msg=f"Updated {key} in {file_path}", debug=debug_logs)
        else:
            debug_logs.append("No changes needed. Exiting without modifying the file.")
            module.exit_json(changed=False, msg=f"No changes needed for {key}", debug=debug_logs)

    except Exception as e:
        debug_logs.append(f"Error occurred: {str(e)}")
        module.fail_json(msg=f"Error updating the file: {str(e)}", debug=debug_logs)

if __name__ == "__main__":
    main()

