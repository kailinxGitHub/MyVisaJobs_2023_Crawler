import re

text = "(Hello), World! (How are you?)"

# Replace only the brackets in the text
clean_text = re.sub(r'[(\[\])]', '', text)

print(clean_text) 

# Compile the pattern to remove brackets
name_pattern = re.compile(r'[(\[\])]')

# Remove brackets from the text
clean_text = name_pattern.sub('', text)

# Search for the matched string
uni_name = re.search(r'[a-zA-Z\s]+', clean_text).group()

print(uni_name)  # Output: Hello, World! (How are you?)