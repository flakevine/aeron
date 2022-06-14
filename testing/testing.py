from aeron.core import connect, Field, Table, Database

#
# usuarios_fieldlist = [Field(field_name="Id", field_type="INTEGER", is_primary_key=True),
#                       Field(field_name="Nome", field_type="TEXT", field_max_length=100),
#                       Field(field_name="Idade", field_type="INTEGER")]
#
#
# db = Database(tables=[], insta_scaffold=True)


db = connect('database.sqlite')

# index = db.get_table_index("Usuarios")
#
# print(db.get_table_fieldnames(index))
#
# print(db.update_one_tuple(index, 1, {"Idade": 100}))

