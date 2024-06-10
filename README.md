## Testy do pokazania

### Kolejka

users

- new user
  - git
    {"kind": "NEW_USER","data": {"login":"new_user10","email":"ur10@mo.m","wallet":21.37}}
  - istnieje
    {"kind": "NEW_USER","data": {"login":"new_user10","email":"ur10@mo.m","wallet":21.37}}
- update info
  - git
    {"kind": "UPDATED_INFO","data": {"login":"new_user10","email":"adam.naworski2000@gmail.com","wallet":21.37}}
  - nie istnieje
    {"kind": "UPDATED_INFO","data": {"login":"new_user10000000000","email":"adam.naworski2000@gmail.com","wallet":21.37}}
- zmiana portfela
  - git
    {"kind": "CHANGED_WALLET_STATE","data": {"login":"new_user10","change_amount":21.37}}
  - nie istnieje
    {"kind": "CHANGED_WALLET_STATE","data": {"login":"new_user10000000000","change_amount":21.37}}
  - uemny stan konta
    {"kind": "CHANGED_WALLET_STATE","data": {"login":"new_user10","change_amount":-2100.37}}
- nieznana akcja
  {"kind": "INVALID_ACTION","data": {"login":"new_user10","email":"ur10@mo.m","wallet":21.37}}

tests

- FINISHED_ANAYZE
  - git
    {"kind": "FINISHED_ANALYZE","data": {"id": 1, "fk_user":"new_user10","analyzer":"121121","examination_date":"2024-05-03 23:54:48.197062","leukocytes":"2137","nitrite":"aak","urobilinogen":"4.6","protein":null,"ph":null,"blood":"0.2","specific_gravity":null,"ascorbate":null,"ketone":null,"bilirubin":null,"glucose":"5.2","micro_albumin":null}}
  - niepoprawne dane
    {"kind": "FINISHED_ANALYZE","data": {"id": 5, "fk_user":"new_user10","analyzer":"121121","examination_date":"2024-05-03 23:54:48.197062","leukocytes":"2137","nitrite":"aak","urobilinogen":"4.6","protein":null,"ph":null,"blood":"1","specific_gravity":null,"ascorbate":null,"ketone":null,"bilirubin":null,"glucose":"5.2","micro_albumin":""}}
  - badanie nie istnieje
    {"kind": "FINISHED_ANALYZE","data": {"id": 1000000000, "fk_user":"new_user10","analyzer":"121121","examination_date":"2024-05-03 23:54:48.197062","leukocytes":"2137","nitrite":"aak","urobilinogen":"4.6","protein":null,"ph":null,"blood":"0.2","specific_gravity":null,"ascorbate":null,"ketone":null,"bilirubin":null,"glucose":"5.2","micro_albumin":null}}

### API

1. get results
   - nie istnieje
   - 0
2. websocket
3. verify customer

   - ok
   - zły token
     3,5 przesłanie wynikóœ kafka

4. get results
5. delete
   - git
   - nie istnieje

- deleted user kafka
  - git
    {"kind": "DELETED","data": {"login":"new_user10","email":"ur10@mo.m","wallet":21.37}}
  - niesitnieje
    {"kind": "DELETED","data": {"login":"new_user10000000000000","email":"ur10@mo.m","wallet":21.37}}
