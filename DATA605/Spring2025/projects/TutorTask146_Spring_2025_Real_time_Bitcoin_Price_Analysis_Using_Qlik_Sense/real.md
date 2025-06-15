## Workflow & Architecture

### High-Level Workflow

```mermaid
graph TD
    A[Python Script: Fetch Bitcoin Price via CoinGecko API] --> B[Write Data to CSV]
    B --> C[Push CSV Files to GitHub]
    C --> D[Qlik Sense REST Connector: Pull Latest CSV from GitHub]
    D --> E[Qlik Sense Dashboard: Visualize & Analyze Data]
    E --> F[User Exploration: Filtering, Analytics, Interactive Charts]
    style A fill:#bbf,stroke:#222,stroke-width:2px
    style E fill:#cfc,stroke:#222,stroke-width:2px
    style F fill:#ffe,stroke:#222,stroke-width:1px
