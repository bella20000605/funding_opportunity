# funding_opportunity

There are a few steps:

      # Step 1: Install Poetry
          python -m pip install --upgrade pip
          pip install poetry

      # Step 2: Install dependencies using Poetry
          poetry install

      # Step 3: Run the scraper Python script using Poetry
          poetry run python funding_opportunity/grants_gov_scraper.py

      # Step 4: Run the email-sending Python script using Poetry
      # (sender = os.getenv('SENDER_EMAIL', 'js5081@georgetown.edu') you can change sender email to your own email to see what happened
          poetry run python funding_opportunity/send_email.py
