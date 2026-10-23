-- Example Lua Script for LAST Serial Terminal
-- This script demonstrates the available functions and event handlers

-- Global variables for script state
local message_count = 0
local connection_time = 0
local rx_buffer = ""

-- Process one complete line (an NMEA sentence or other text)
local function handle_line(line)
    message_count = message_count + 1

    -- Log received line with count
    log("Received message #" .. message_count .. ": " .. line)

    -- Check if it's an NMEA sentence
    if string.sub(line, 1, 1) == "$" then
        local parsed = parse_nmea(line)
        if parsed and parsed.talker and parsed.type then
            log("NMEA sentence parsed: " .. parsed.talker .. parsed.type ..
                " (" .. #(parsed.fields or {}) .. " fields)")
        end
    end

    -- Auto-respond to specific commands
    if string.find(line, "PING") then
        send("PONG\r\n")
        log("Auto-responded with PONG")
    end
end

-- Called when data is received from the serial connection.
-- Data arrives in arbitrary chunks (a sentence may be split across calls,
-- or one call may hold several), so buffer it and handle complete lines.
function on_data_received(data)
    rx_buffer = rx_buffer .. data

    for line in string.gmatch(rx_buffer, "([^\r\n]*)\r?\n") do
        if #line > 0 then
            handle_line(line)
        end
    end

    -- Keep any trailing partial line for the next chunk
    rx_buffer = string.match(rx_buffer, "[^\n]*$")

    -- Return nil to allow normal processing
    return nil
end

-- Called before data is sent through the connection
function on_data_send(data)
    log("Sending: " .. data)
    
    -- You could modify the data here before sending
    -- For example, add a timestamp or checksum
    
    -- Return nil to send original data, or return modified data
    return nil
end

-- Called when connection is established
function on_connection_open()
    connection_time = os.time()
    log("Connection opened at " .. os.date("%Y-%m-%d %H:%M:%S", connection_time))
    
    -- Get connection info
    local info = get_connection_info()
    if info then
        log("Connection details: " .. info.type .. " - " .. tostring(info.port))
    end
    
    -- Send a welcome message after 1 second (simulated)
    -- Note: In a real implementation, you might want to use a timer
    -- send("Welcome! Lua scripting is active.\r\n")
end

-- Called when connection is closed
function on_connection_close()
    local duration = os.time() - connection_time
    log("Connection closed after " .. duration .. " seconds")
    log("Total messages processed: " .. message_count)
    
    -- Reset counters
    message_count = 0
    connection_time = 0
end

-- Example function to create an NMEA sentence
function create_test_nmea()
    local nmea = create_nmea("GP", "GGA", {"123456.00", "4807.038", "N", "01131.000", "E",
                                                 "1", "08", "0.9", "545.4", "M", "46.9", "M", "", ""})
    if nmea then
        log("Created NMEA sentence: " .. nmea)
        return nmea
    end
    return nil
end

-- Example function to demonstrate statistics
function show_stats()
    local stats = get_statistics()
    if stats then
        log("Statistics - Sent: " .. stats.bytes_sent .. ", Received: " .. stats.bytes_received)
    end
end

-- Utility function for logging with timestamp
function log_with_time(message)
    log("[" .. os.date("%H:%M:%S") .. "] " .. message)
end

log("Lua script loaded successfully!")
