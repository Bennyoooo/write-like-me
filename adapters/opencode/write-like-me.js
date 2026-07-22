export const WriteLikeMe = async () => ({
  "chat.message": async (_input, output) => {
    try {
      const child = Bun.spawn(["wlm", "hook", "--agent", "opencode"], {
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
