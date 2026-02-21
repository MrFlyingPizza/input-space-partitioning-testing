categories = [
    ["None", "One", "Many"], # Input file count
    ["SomeNoExist", "SomeReadProtected", "AllValid"], # Input files characteristics
    ["YesStdin", "NoStdin"], 
    ["None", "One", "Many"], # Input stdin or file line amount
    ["AllEmpty", "SomeEmpty", "NoneEmpty"], # Input stdin or file line emptiness
    ["RandomChars", "Months", "NumericOnly", "HumanReadableNumbers", "VersionNumbers"], # Input file or stdin content type
    ["OnlyOne", "AtLeastOne"], # Number of characters per line
    ["All", "Some", "None"], # Lines with leading blanks
    ["ASCII", "UTF-8", "UTF-16"], # Character encoding of input file or stdin
    ["Ascending", "Descending", "Unsorted"], # Order of stdin or file input lines
    [True, False],  # Ignore Leading Blanks
    [True, False],  # Dictionary Order
    [True, False],  # Ignore Case
    [True, False],  # Ignore Non-printable Characters
    ["Month", "Numeric", "HumanNumeric", "Random", "Version"], # Sort type
    [True, False],  # Sort in Reverse
    ["None", "NoExist", "Empty", "ReadProtected", "Valid"] # Random source file
]

