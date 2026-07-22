export const WriteLikeMe = async () => ({
  "chat.message": async (_input, output) => {
    try {
      const home = process.env.WLM_HOME || `${process.env.HOME}/.write-like-me`;
      const executable = Bun.which("wlm") || `${home}/runtime/bin/wlm`;
      const child = Bun.spawn([executable, "hook", "--agent", "opencode"], {
        stdin: "pipe",
        stdout: "ignore",
        stderr: "ignore",
      });
      child.stdin.write(JSON.stringify(output));
      child.stdin.end();
      await child.exited;
    } catch {
      // Capture must never interrupt the agent.
    }
  },
});
