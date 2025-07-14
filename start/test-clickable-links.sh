#!/bin/bash

# Test script for Cmd+Click terminal links in macOS Terminal.app

echo "🔗 Testing Cmd+Click Terminal Links (macOS)"
echo ""

echo "Terminal Support:"
echo "✅ Terminal.app: Cmd+Click on URLs"
echo "✅ iTerm2: Cmd+Click on URLs"  
echo "✅ Most terminals: Auto-detect file:// and https:// URLs"
echo ""

echo "Test Links (use Cmd+Click):"
echo "🌐 Web URL: https://claude.ai/code"
echo "📝 File URL: file://$(pwd)"
echo "📋 Dashboard: https://supabase.com/dashboard"
echo ""

echo "Instructions:"
echo "1. Hold Cmd and click on any URL above"
echo "2. file:// URLs will open in Finder"
echo "3. https:// URLs will open in your default browser"