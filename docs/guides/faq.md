# Frequently Asked Questions

Common questions and answers about the Expense Tracker application.

## General Questions

### Q: What is the Expense Tracker?
A: The Expense Tracker is a comprehensive financial management application that helps you track expenses, manage accounts, create budgets, and analyze your spending patterns.

### Q: Is the application free?
A: Yes, the Expense Tracker is open-source and completely free to use and modify.

### Q: What browsers are supported?
A: The application supports all modern browsers including Chrome, Firefox, Safari, and Edge.

### Q: Can I use this application offline?
A: The web application requires an internet connection for the initial setup, but basic functionality works offline once loaded.

## Installation & Setup

### Q: Do I need to install MongoDB separately?
A: Yes, MongoDB is required as the database backend. You can install it locally or use a cloud MongoDB service.

### Q: Can I use a different database?
A: Currently, only MongoDB is supported. Future versions may include support for PostgreSQL and MySQL.

### Q: How do I reset my password?
A: Use the "Forgot Password" feature on the login page, or reset it via the command line:
```bash
python manage.py reset-password <email>
```

### Q: Can I run multiple instances of the application?
A: Yes, but you'll need to use different ports and databases for each instance.

## Data & Privacy

### Q: Where is my data stored?
A: Your data is stored locally in your MongoDB database. No data is sent to external servers.

### Q: Is my data encrypted?
A: Data is encrypted in transit (HTTPS) and can be encrypted at rest using MongoDB's encryption features.

### Q: Can I export my data?
A: Yes, you can export your data in CSV, JSON, or Excel formats from the Settings page.

### Q: How do I backup my data?
A: Use the built-in backup feature or manually backup your MongoDB database:
```bash
mongodump --db expense_tracker --out /path/to/backup
```

## Features & Usage

### Q: Can I track multiple currencies?
A: Yes, the application supports multiple currencies with automatic exchange rate updates.

### Q: How do I create recurring transactions?
A: Go to Transactions → Add Transaction → Enable "Recurring" option and set the frequency.

### Q: Can I share my data with others?
A: Currently, the application is single-user. Multi-user support is planned for future releases.

### Q: How are budgets calculated?
A: Budgets are calculated based on the sum of transactions in each category within the specified time period.

### Q: Can I customize categories?
A: Yes, you can create, edit, and delete categories from the Categories page.

## Technical Questions

### Q: What's the API rate limit?
A: The API is limited to 100 requests per minute per IP address.

### Q: Can I use the API for mobile apps?
A: Yes, the RESTful API can be used to build mobile applications.

### Q: How do I enable debug mode?
A: Set `FLASK_ENV=development` and `DEBUG=True` in your `.env` file.

### Q: What's the maximum file size for imports?
A: The maximum import file size is 50MB.

## Troubleshooting

### Q: The application won't start
A: Check the following:
1. MongoDB is running
2. Python dependencies are installed
3. Environment variables are set correctly
4. Port 5000 is not in use

### Q: I'm getting database connection errors
A: Verify your MongoDB connection string in the `.env` file and ensure MongoDB is accessible.

### Q: My transactions aren't showing up
A: Check your date filters and ensure you're looking at the correct time period.

### Q: The dashboard charts aren't loading
A: Ensure you have JavaScript enabled and check the browser console for errors.

## Performance & Scaling

### Q: How many transactions can the application handle?
A: The application can handle hundreds of thousands of transactions efficiently.

### Q: Is there a limit on the number of accounts?
A: No, you can create unlimited accounts.

### Q: How can I improve performance?
A: Regular database maintenance, proper indexing, and caching can improve performance.

## Integration

### Q: Can I import data from other expense trackers?
A: Yes, you can import CSV files from most expense tracking applications.

### Q: Does it integrate with banks?
A: Direct bank integration is not available, but you can import bank statements in CSV format.

### Q: Can I use this with accounting software?
A: Yes, you can export data in formats compatible with QuickBooks, Xero, and other accounting software.

## Security

### Q: How secure is my data?
A: The application uses industry-standard security practices including password hashing, JWT tokens, and HTTPS encryption.

### Q: Can I enable two-factor authentication?
A: Two-factor authentication is planned for a future release.

### Q: How often should I update?
A: We recommend updating to the latest stable version as soon as it's available.

## Still Have Questions?

If your question isn't answered here:
1. Check the [troubleshooting guide](./troubleshooting.md)
2. Search existing GitHub issues
3. Create a new issue with detailed information
4. Join our community forum for community support
