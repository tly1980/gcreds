![supported python versions](python-2.7%203.4%203.5%203.6-blue.svg)
# gcreds

Inspired by [credstash](https://github.com/fugue/credstash),  I ended up putting datastore and [Google Cloud KMS (CLOUD KEY MANAGEMENT SERVICE)](https://cloud.google.com/kms/) together to make `gcreds` to manage credentials in google cloud.

`gcreds` allows you store (put) and access (get) your credential in google cloud, and help to reduce security hole like keeping secrets being stored from your source code control.

## Installation

Just run:

```
pip install gcreds
```

## Getting started

Before you can use it, it will require a little setup work here:

1. Greate a KMS key ring on `global` location, named it like `gcreds`.
2. Under that key ring, create a crypto key named `gcreds`.

You can customized `location`, `key-ring`, `cryopto-key`.

Once you have it setup, let's try to put some credential.

Storing the password:

```
$ ./gcreds.py put mysecret SxtlB5fBvvAKT7P4
project_id is not provided, will use default project: [your-default-gcloud-project] instead.
```

Retriving the password:

```
$ ./gcreds.py get mysecret
project_id is not provided, will use default project: [your-default-gcloud-project] instead.
SxtlB5fBvvAKT7P4
```

You can also redirect a file to it.

Let's have a file contain a super strong password by hand.

```
$ cat a_super_password.txt
Y#7U*ubwZh=D^XEq3a_MMyX3NVL_gfk9K4eq2HX
```

And Let's use the redirect to enter the password

```
$ ./gcreds.py put mysecret < a_super_password.txt
project_id is not provided, will use default project: [tom-finance] instead.

```

Let's retrive the password

```
$ ./gcreds.py get mysecret
project_id is not provided, will use default project: [tom-finance] instead.
Y#7U*ubwZh=D^XEq3a_MMyX3NVL_gfk9K4eq2HX
```

