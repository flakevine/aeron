from skl.orm import connect

# usuarios_fieldlist = [Field(field_name="Id", field_type="INTEGER", is_primary_key=True),
#                       Field(field_name="Nome", field_type="TEXT", field_max_length=100),
#                       Field(field_name="Idade", field_type="INTEGER")]
#
# usuarios = Table(table_name="Usuarios", fields=usuarios_fieldlist)
# db = Database(tables=[usuarios], insta_scaffold=True)

db = connect('database.sqlite')

index = db.get_table_index("Usuarios")

fieldnames = db.get_table_fieldnames(index)

print(db.delete_one_tuple(table_index=index, tuple_id=3))
