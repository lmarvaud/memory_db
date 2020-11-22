# Contrib

1. fork the repository

2. clone your forked repository locally

3. *optional :* create a virtualenv
    ```
    python -m virtualenv ./venv
    source ./venv/bin/activate
    ```

4. init local environement
    ```
    make init
    ```

5. contribute

6. unsure project quality
    ```
    make mypy yapf flake8 coverage
    ```

7. create a pull request
