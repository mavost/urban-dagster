
dagster_project/
├── checks/
│   └── sales-dwh/
│       ├── flyway_dev.conf
│       ├── flyway_test.conf
│       ├── flyway_prod.conf
│       └── sql/
│           ├── V1__baseline.sql
│           └── V2__add_errorcode.sql
├── .env                       # holds DB creds
├── flyway_dagster.py         # contains the Dagster job + ops
└── repo.py                   # Dagster entrypoint
