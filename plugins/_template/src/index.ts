const PLUGIN_ID = "my-plugin";

/** Minimal register entry — replace `any` with OpenClawPluginApi when openclaw is a dep. */
export default function register(api: {
  logger: { info: (...args: unknown[]) => void };
}) {
  api.logger.info(`[${PLUGIN_ID}] registered`);

  // Example: register a chat command
  // api.registerCommand({
  //   name: "hello",
  //   description: "Say hello",
  //   handler: async () => ({ text: "Hello from my-plugin" }),
  // });
}
