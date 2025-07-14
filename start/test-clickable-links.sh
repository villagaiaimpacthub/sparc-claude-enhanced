#!/bin/bash

# Test script for clickable terminal links
# This demonstrates OSC 8 hyperlink sequences

echo "🔗 Testing Clickable Terminal Links"
echo ""

# Helper function to create clickable links
make_clickable() {
    local url="$1"
    local text="${2:-$url}"
    echo "\033]8;;${url}\033\\${text}\033]8;;\033\\"
}

echo "Terminal Support:"
echo "✅ iTerm2, Terminal.app (macOS)"
echo "✅ GNOME Terminal, Konsole (Linux)"  
echo "✅ Windows Terminal"
echo "✅ VS Code Integrated Terminal"
echo ""

echo "Test Links:"
echo "🌐 Web URL: $(make_clickable "https://claude.ai/code" "Claude Code Download")"
echo "📝 File URL: $(make_clickable "file://$(pwd)" "Current Directory")"
echo "📋 Dashboard: $(make_clickable "https://supabase.com/dashboard" "Supabase Dashboard")"
echo ""

echo "If your terminal supports OSC 8 sequences, these should be clickable!"
echo "If not, they'll appear as regular text with underlying URLs."