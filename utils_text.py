def preprocess_text(input_text):
    lines = input_text.split('\n')
    variables = []

    for line in lines:
        # Split each line into number and name
        parts = line.split('. ')
        if len(parts) == 2:
            number, name = parts
            # Remove leading/trailing whitespaces and replace spaces with underscores
            variable_name = name.strip().replace(' ', '_')
            # Ensure the variable name is a valid Python variable
            variable_name = ''.join(filter(str.isidentifier, variable_name))
            # Append the variable name to the list
            variables.append(f"{variable_name}")

    # Join the processed variables into a Python script
    #python_script = '\n'.join(variables)

    return variables

# Example usage
input_text = """1. Rigi Mountain
2. Chapel Bridge
3. Swiss Museum of Transport
4. Lake Zug
5. Hertenstein Castle
6. Old Town of Zug
7. Lindt Chocolate Factory Outlet
8. Sihlwald Wildlife Park
9. Uetliberg Mountain
10. Bahnhofstrasse shopping street"""

python_script = preprocess_text(input_text)
print(python_script)
