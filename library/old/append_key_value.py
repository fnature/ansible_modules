#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule

def main():
    module_args = dict(
        file_path=dict(type='str', required=True),
        key=dict(type='str', required=True),
        value=dict(type='list', elements='str', required=True),
        delimiter=dict(type='str', required=False, default="="),  # Default delimiter is '='
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    file_path = module.params['file_path']
    key = module.params['key']
    values = module.params['value']
    delimiter = module.params['delimiter']

    try:
        # Read the file if it exists
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
        except FileNotFoundError:
            lines = []

        found_key = False
        updated_lines = []

        # Process the file line by line
        for line in lines:
            # Check if the line starts with 'key=' (key followed by equal sign)
            if line.strip().startswith(f"{key}="):
                found_key = True
                # Get the current values after the '=' sign
                current_values = line.strip().split('=', 1)[1].split(delimiter)
                
                # Add values only if they are not already present
                for value in values:
                    if value not in current_values:
                        current_values.append(value)
                
                # Reconstruct the line with updated values (no extra '=')
                updated_line = f"{key}{delimiter}{delimiter.join(current_values)}\n"
                updated_lines.append(updated_line)
            else:
                updated_lines.append(line)

        # Add the key if not found
        if not found_key:
            updated_lines.append(f"{key}{delimiter}{delimiter.join(values)}\n")

        # Write changes if needed
        if lines != updated_lines:
            if not module.check_mode:
                with open(file_path, 'w') as file:
                    file.writelines(updated_lines)
            module.exit_json(changed=True, msg=f"Updated {key} in {file_path}")
        else:
            module.exit_json(changed=False, msg=f"No changes needed for {key}")

    except Exception as e:
        module.fail_json(msg=f"Error updating the file: {str(e)}")

if __name__ == "__main__":
    main()

