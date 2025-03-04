#!/usr/bin/env python3
import re
import sys
import subprocess

# Path to your zone file
ZONE_FILE_PATH = "/etc/coredns/dblab.org"

def increment_serial(zone_data):
    """
    Find the serial number in the SOA record and increment it.
    Assumes the serial appears on a line like: "2023021601 ; Serial"
    """
    def replacer(match):
        current_serial = int(match.group(1))
        new_serial = current_serial + 1
        return f"{new_serial} ; Serial"
    
    pattern = r"(\d+)\s*; Serial"
    new_zone_data, count = re.subn(pattern, replacer, zone_data, count=1)
    if count == 0:
        print("Error: Serial number not found in zone file.")
        sys.exit(1)
    return new_zone_data

def update_a_record(zone_data, record_name, ip_address):
    """
    Update an existing A record for record_name or add it if not found.
    """
    record_regex = re.compile(rf"^{record_name}\s+IN\s+A\s+([\d\.]+)", re.MULTILINE)
    if record_regex.search(zone_data):
        # Update the existing record
        zone_data = record_regex.sub(f"{record_name} IN  A   {ip_address}", zone_data)
        print(f"Updated existing record {record_name} to {ip_address}.")
    else:
        # Append the new record at the end of the file
        zone_data += f"\n{record_name} IN  A   {ip_address}\n"
        print(f"Added new record {record_name} with {ip_address}.")
    return zone_data

def delete_a_record(zone_data, record_name):
    """
    Delete an A record for the given record_name.
    """
    record_regex = re.compile(rf"^{record_name}\s+IN\s+A\s+[\d\.]+\s*$", re.MULTILINE)
    new_zone_data, count = record_regex.subn("", zone_data)
    if count > 0:
        print(f"Deleted record {record_name}.")
    else:
        print(f"Record {record_name} not found.")
    return new_zone_data, count

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  To update/add a record: update_zone.py update <record_name> <ip_address>")
        print("  To delete a record:     update_zone.py delete <record_name>")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    # Read the current zone file
    try:
        with open(ZONE_FILE_PATH, "r") as f:
            zone_data = f.read()
    except Exception as e:
        print(f"Error reading zone file: {e}")
        sys.exit(1)
    
    if action == "update":
        if len(sys.argv) != 4:
            print("Usage: update_zone.py update <record_name> <ip_address>")
            sys.exit(1)
        record_name = sys.argv[2]
        ip_address = sys.argv[3]
        zone_data = update_a_record(zone_data, record_name, ip_address)
    elif action == "delete":
        if len(sys.argv) != 3:
            print("Usage: update_zone.py delete <record_name>")
            sys.exit(1)
        record_name = sys.argv[2]
        zone_data, count = delete_a_record(zone_data, record_name)
        if count == 0:
            # If record wasn't found, you might want to treat that as an error.
            sys.exit(1)
    else:
        print("Invalid action. Use 'update' or 'delete'.")
        sys.exit(1)
    
    # Increment the serial number
    zone_data = increment_serial(zone_data)
    
    # Write the updated zone file back
    try:
        with open(ZONE_FILE_PATH, "w") as f:
            f.write(zone_data)
    except Exception as e:
        print(f"Error writing zone file: {e}")
        sys.exit(1)
    
    # Reload CoreDNS to apply changes
    try:
        subprocess.run(["sudo", "systemctl", "rearer", "coredns"], check=True)
        print("Reloaded CoreDNS successfully.")
    except subprocess.CalledProcessError as e:
        print("Error reloading CoreDNS:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
