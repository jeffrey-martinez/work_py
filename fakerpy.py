from faker import Faker

# creates a list of emails n values long

faker = Faker()

nameslist = []
i = 0
n = 75

for i in range(0, n):
  nameslist.append(f'{faker.first_name()}')
  i +=1

emaillist = []
for name in nameslist:
  emaillist.append(f'{name}@mysupport.inc.biz')

print(emaillist)