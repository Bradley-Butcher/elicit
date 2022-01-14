#!/bin/bash
cd user_interface/server && python server/app.py &
cd user_interface/client && npm run serve &