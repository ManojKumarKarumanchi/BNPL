This project implements a real-time BNPL (Buy Now, Pay Later) eligibility system inspired by fintech checkout experiences.

It simulates how platforms like GrabOn can leverage transaction-level behavioral data to underwrite instant credit decisions at the moment of purchase.

The system evaluates user activity (purchase frequency, GMV trends, return behavior, and category diversity) to generate a credit score, determine eligibility, and present EMI options directly within a checkout interface.

Unlike traditional black-box scoring systems, this engine produces clear, human-readable explanations for every decision, making the credit approval process transparent and interpretable.

The end-to-end flow includes:
- Transaction data ingestion via API (MCP-style tool layer)
- Real-time credit scoring engine
- Fraud velocity checks for new users
- EMI offer generation (3/6/9 months)
- AI-generated credit reasoning
- Checkout UI simulation for a production-like experience
