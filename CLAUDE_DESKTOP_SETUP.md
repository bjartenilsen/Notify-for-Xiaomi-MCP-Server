# Claude Desktop Setup Guide

This guide explains how to integrate the Notify Xiaomi MCP Server with Claude Desktop on Windows.

## Prerequisites

Before configuring Claude Desktop, ensure you have:

1. ✅ Python 3.10 or higher installed
2. ✅ Notify Xiaomi MCP Server installed (see main README.md)
3. ✅ Google Drive credentials configured (`~/.notify-xiaomi-mcp/credentials.json`)
4. ✅ Claude Desktop installed on Windows

## Configuration Steps

### Step 1: Locate Claude Desktop Configuration File

The Claude Desktop configuration file is located at:

```
%APPDATA%\Claude\claude_desktop_config.json
```

To open this location:
1. Press `Win + R` to open the Run dialog
2. Type `%APPDATA%\Claude` and press Enter
3. Look for `claude_desktop_config.json` (create it if it doesn't exist)

### Step 2: Find Your Python Path

You need the full path to your Python executable. Open Command Prompt and run:

```cmd
where python
```

This will output something like:
```
C:\Users\YourUsername\AppData\Local\Programs\Python\Python310\python.exe
```

**Note**: If you're using a virtual environment, use the Python path from your venv:
```
C:\path\to\notify-xiaomi-mcp-server\venv\Scripts\python.exe
```

### Step 3: Find Your Server Path

You need the full path to `server.py`. If you cloned the repository to your home directory:

```
C:\Users\YourUsername\notify-xiaomi-mcp-server\src\server.py
```

### Step 4: Edit Configuration File

Open `claude_desktop_config.json` in a text editor (Notepad, VS Code, etc.) and add the server configuration:

```json
{
  "mcpServers": {
    "notify-xiaomi": {
      "command": "python",
      "args": [
        "C:\\Users\\YourUsername\\notify-xiaomi-mcp-server\\src\\server.py"
      ]
    }
  }
}
```

**Important**: 
- Use double backslashes (`\\`) in Windows paths
- Replace `YourUsername` with your actual Windows username
- Replace the path with your actual installation path

### Step 5: Using Virtual Environment (Recommended)

If you installed the server in a virtual environment, use the venv's Python:

```json
{
  "mcpServers": {
    "notify-xiaomi": {
      "command": "C:\\Users\\YourUsername\\notify-xiaomi-mcp-server\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\YourUsername\\notify-xiaomi-mcp-server\\src\\server.py"
      ]
    }
  }
}
```

### Step 6: Restart Claude Desktop

After saving the configuration file:
1. Close Claude Desktop completely (check system tray)
2. Restart Claude Desktop
3. The Notify Xiaomi tools should now be available

## Verifying the Setup

Once Claude Desktop restarts, you can verify the integration by asking Claude:

```
What MCP tools are available?
```

You should see the six Notify Xiaomi tools listed:
- `nxk_sync_database`
- `nxk_list_tables`
- `nxk_get_sleep`
- `nxk_get_heart_rate`
- `nxk_get_activity`
- `nxk_query`

## Testing the Connection

Try syncing the database:

```
Please use the nxk_sync_database tool to download my health data from Google Drive.
```

On first run, this will:
1. Open a browser window for Google OAuth2 authentication
2. Ask you to grant read-only access to your Google Drive
3. Download the backup.db file
4. Save the authentication token for future use

## Configuration Examples

### Example 1: Basic Configuration

```json
{
  "mcpServers": {
    "notify-xiaomi": {
      "command": "python",
      "args": [
        "C:\\Users\\John\\notify-xiaomi-mcp-server\\src\\server.py"
      ]
    }
  }
}
```

### Example 2: With Virtual Environment

```json
{
  "mcpServers": {
    "notify-xiaomi": {
      "command": "C:\\Users\\John\\notify-xiaomi-mcp-server\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\John\\notify-xiaomi-mcp-server\\src\\server.py"
      ]
    }
  }
}
```

### Example 3: Multiple MCP Servers

If you have other MCP servers configured:

```json
{
  "mcpServers": {
    "notify-xiaomi": {
      "command": "python",
      "args": [
        "C:\\Users\\John\\notify-xiaomi-mcp-server\\src\\server.py"
      ]
    },
    "another-server": {
      "command": "node",
      "args": [
        "C:\\path\\to\\another-server\\index.js"
      ]
    }
  }
}
```

### Example 4: With Environment Variables (Optional)

If you need to set environment variables:

```json
{
  "mcpServers": {
    "notify-xiaomi": {
      "command": "python",
      "args": [
        "C:\\Users\\John\\notify-xiaomi-mcp-server\\src\\server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Troubleshooting

### Issue: Tools Not Appearing in Claude Desktop

**Solution**:
1. Verify the configuration file path is correct: `%APPDATA%\Claude\claude_desktop_config.json`
2. Check JSON syntax is valid (use a JSON validator)
3. Ensure paths use double backslashes (`\\`)
4. Restart Claude Desktop completely
5. Check Claude Desktop logs for errors

### Issue: "Python not found" Error

**Solution**:
- Use the full path to python.exe instead of just "python"
- Example: `"command": "C:\\Python310\\python.exe"`

### Issue: "Module not found" Error

**Solution**:
- Ensure you installed dependencies: `pip install -e .`
- If using a virtual environment, use the venv's Python path in the command field

### Issue: Server Starts But Tools Don't Work

**Solution**:
1. Check that credentials.json exists at `~/.notify-xiaomi-mcp/credentials.json`
2. Run the server manually to see error messages:
   ```cmd
   python C:\path\to\server.py
   ```
3. Verify Google Drive API is enabled in your Google Cloud project

### Issue: Authentication Window Doesn't Open

**Solution**:
- The OAuth2 flow requires a browser
- Ensure you're running Claude Desktop with GUI access (not as a service)
- Check that port 0 (random port) is available for the OAuth callback

## Transport Configuration

The Notify Xiaomi MCP Server uses **stdio transport**, which means:

- **Standard Input (stdin)**: Receives MCP protocol messages from Claude Desktop
- **Standard Output (stdout)**: Sends MCP protocol responses to Claude Desktop
- **Standard Error (stderr)**: Logs errors and diagnostic information

This is the standard transport method for MCP servers and requires no additional configuration beyond the command and args fields.

## Security Notes

1. **Read-Only Access**: The server only requests read-only access to Google Drive
2. **Local Storage**: Authentication tokens are stored locally in `~/.notify-xiaomi-mcp/token.pickle`
3. **Database Safety**: All database operations are read-only; your backup data cannot be modified
4. **Query Validation**: Only SELECT queries are allowed; write operations are blocked

## File Locations

After setup, you'll have these files:

```
~/.notify-xiaomi-mcp/
├── credentials.json      # OAuth2 credentials (you provide this)
├── token.pickle          # Authentication token (auto-generated)
└── backup.db            # Downloaded database (auto-generated)
```

On Windows, `~/.notify-xiaomi-mcp/` expands to:
```
C:\Users\YourUsername\.notify-xiaomi-mcp\
```

## Next Steps

After successful configuration:

1. **Sync your database**: Use `nxk_sync_database` to download the latest backup
2. **Explore your data**: Use `nxk_list_tables` to see available tables
3. **Query health metrics**: Use the specific tools for sleep, heart rate, and activity data
4. **Custom queries**: Use `nxk_query` for advanced data exploration

## Additional Resources

- [Main README](README.md) - Installation and usage guide
- [MCP Protocol Documentation](https://modelcontextprotocol.io/) - Learn about MCP
- [Google Drive API Setup](https://developers.google.com/drive/api/quickstart/python) - OAuth2 credentials guide

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Test the server manually from command line
4. Check Claude Desktop logs for error messages
5. Ensure all file paths are correct with double backslashes

## Configuration Validation Checklist

Before restarting Claude Desktop, verify:

- [ ] JSON syntax is valid (no trailing commas, proper quotes)
- [ ] Python path exists and is correct
- [ ] Server.py path exists and is correct
- [ ] All backslashes are doubled (`\\`)
- [ ] File is saved as `claude_desktop_config.json`
- [ ] File is in `%APPDATA%\Claude\` directory

Once all items are checked, restart Claude Desktop and test the integration!
