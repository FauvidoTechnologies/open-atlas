# Tools

The following tools are available to the Atlas:

1. Firmware analysis
2. Deepfake detection
3. Facial comparisions
4. Face attribute analysis
5. Email verification
6. Browser automation
7. Reddit username based searches
8. Reddit username extraction searches

# Browser automation

Headless browser automations is a tool different from the others. This tool can be invoked only be the `UpperAgent` directly and there are no functions present inside which can be called on by the `LowerAgent`.

This is because browser automation acts as its own operation since its pretty complex. For an exact representation of how the flow happens between the central brain and browser automations, refer to the flow diagram below.

![flow diagram](../../images/browser_automation_flow_control.png)