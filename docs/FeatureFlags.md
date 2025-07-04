# Feature flags

Walbot supports a small set of feature flags that can be enabled via environment variables.
These flags toggle optional or experimental functionality. Set them before starting the bot.

| Flag | Effect |
| --- | --- |
| `WALBOT_TEST_AUTO_UPDATE` | Forces autoupdate to run every 10 minutes and apply updates even when there are none. Useful for testing autoupdate behaviour. |
| `WALBOT_FEATURE_MARKOV_MONGO` | Stores Markov chains in MongoDB instead of the local `markov.yaml` file. Requires a MongoDB database. This feature is experimental and not recommended for production use. |

To enable a flag, set it to `1` or `ON`.
