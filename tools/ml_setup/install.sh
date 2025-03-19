#!/usr/bin/env bash

# Define variables to exclude
EXCLUDE_VARS="PWD|LANG|PYTHONPATH|ROOT|PS0|PS1|PS2|_|OLDPWD|LC_ALL|LANG|LSCOLORS|SHLVL|TZ"


echo "Original Environment Variables:"
env | sort

# Add standalone python3 & pip3 from swe-rex to PATH
export PATH="/root/python3.11/bin:$PATH"

# Attempt to read and set process 1 environment
echo -e "\nSetting environment variables from /proc/1/environ..."
if [ -r "/proc/1/environ" ]; then
    while IFS= read -r -d '' var; do
        # Skip excluded variables
        if ! echo "$var" | grep -qE "^(${EXCLUDE_VARS})="; then
            # If the variable is PATH, append and deduplicate
            if [[ "$var" =~ ^PATH= ]]; then
                # Combine paths and remove duplicates while preserving order
                export PATH="$(echo "${PATH}:${var#PATH=}" | tr ':' '\n' | awk '!seen[$0]++' | tr '\n' ':' | sed 's/:$//')"
            else
                export "$var"
            fi
        fi
    done < /proc/1/environ
    echo "Successfully imported environment from /proc/1/environ"
else
    echo "Cannot access /proc/1/environ - Permission denied"
fi

# Print updated environment variables
echo -e "\nUpdated Environment Variables:"
env | sort
