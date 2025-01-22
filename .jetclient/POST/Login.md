```toml
name = 'Login'
method = 'POST'
url = 'http://localhost:8000/api/auth/login'
sortWeight = 1000000
id = 'a28588c8-b380-42f8-868a-3c462eeb467f'

[[headers]]
key = 'X-CSRFToken'
value = '0dJKlH9pBEGVF2yfoIf4Studlmta9ggx'

[[body.formData]]
key = 'email'
value = 'doe.jon@gmail.com'

[[body.formData]]
key = 'password'
value = '1'

[[body.formData]]
key = 'csrftoken'
value = '0dJKlH9pBEGVF2yfoIf4Studlmta9ggx'
```
