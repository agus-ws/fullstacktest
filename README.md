# FULLSTACK TEST


## Get started

### How to run api
```
$ cd graphql_api
$ virtualenv venv --python=python3
$ source venv/bin/activate
$ (venv) python manage.py migrate
$ (venv) python manage.py seed
$ (venv) python manage.py runserver 8200
```

Go to `http://localhost:8200/graphql` to play around with the example api. Try execute this query
```
query {
  transactions {
    pk
    category
    amount
    createdAt
  }
}
```

### GraphQL Mutations

#### 1. Create wallet

```
mutation {
  createWallet(name: "john", balance: "100") {
    wallet {
      id
      pk
      name
      balance
      createdAt
    }
  }
}
```


#### 2. Create transaction

```
mutation {
  createTransaction(
    sourceWalletPk: "5757696552"
    targetWalletPk: "2436835222"
    amount: 10
    category: ENGINEERING
  ) {
    transaction {
      id
      pk
      amount
      category
      createdAt
      records {
        edges {
          node {
            id
            pk
            wallet {
              id
              pk
              name
              balance
            }
            debitAmount
            creditAmount
          }
        }
      }
    }
  }
}
```

### GraphQL Queries

#### 1. Get wallet by id with transaction records and monthly transactions

```
query {
  wallet(id: "V2FsbGV0Tm9kZToyNDM2ODM1MjIy") {
    id
    pk
    name
    balance
    createdAt
    transactionRecords {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          pk
          debitAmount
          creditAmount
          transaction {
            id
            pk
            category
            createdAt
          }
        }
      }
    }
    monthlyTransactions(month: 11, year: 2023) {
      id
      pk
      debitAmount
      creditAmount
      transaction {
        id
        pk
        category
        createdAt
      }
    }
  }
}

```

#### 2. Get all wallets (filterable using django-filter)

```
query {
  wallets {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    edges {
      node {
        id
        pk
        name
        balance
        updatedAt
        createdAt
      }
    }
  }
}
```

#### 3. Get dormant wallets (1 year inactivity)

```
query {
  dormantWallets {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    edges {
      node {
        id
        pk
        name
        balance
        updatedAt
        createdAt
      }
    }
  }
}
```

#### 4. Get transaction by id

```
query {
  transaction(
    id: "VHJhbnNhY3Rpb25Ob2RlOjFkNjkwNTZhLTc0Y2QtNDA2Yi1iMTljLTQxMmJmNTRmNGQ4MQ=="
  ) {
    id
    pk
    amount
    category
    createdAt
    records {
      edges {
        node {
          id
          pk
          wallet {
            id
            pk
            name
            balance
          }
          debitAmount
          creditAmount
        }
      }
    }
  }
}

```

#### 5. Get all transactions (filterable using django-filter)

```
query {
  transactions {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    edges {
      node {
        id
        pk
        amount
        category
        createdAt
      }
    }
  }
}
```

#### 6. Get transaction record by id

```
query {
  transactionRecord(
    id: "VHJhbnNhY3Rpb25SZWNvcmROb2RlOmFjY2ExNzRmLTc3NjAtNGEyYy1iZjE5LTI4YTMyNDZiNTAxZQ=="
  ) {
    id
    pk
    debitAmount
    creditAmount
    wallet {
      id
      pk
      name
      balance
      updatedAt
    }
  }
}
```

#### 7. Get all transaction records

```
query {
  transactionRecords{
    edges {
      node {
        id
        pk
        debitAmount
        creditAmount
        wallet{
          id
          pk
          name
          balance
          updatedAt
        }
      }
    }
  }
}
```

### How to run test for backend

```
$ cd graphql_api
$ source venv/bin/activate
$ (venv) pytest
```

### How to run frontend

Open new terminal
```
$ cd frontend
$ npm install
$ npm run app
```
