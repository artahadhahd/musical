with open(__file__, 'w') as file:
    file.write(
"""
print('hello, world')
with open(__file__) as file:
    exec(file.read())
""")
with open(__file__, 'r') as file:
    exec(file.read())
