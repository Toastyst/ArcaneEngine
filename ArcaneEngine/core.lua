local ADDON_NAME = "ArcaneEngine"

local Frame = CreateFrame("Frame", "ArcaneEngineFrame")

local function Print(msg)
    print("[ArcaneEngine] " .. msg)
end

local function HandleArcane(input)
    input = (input or ""):lower():gsub("^%s*(.-)%s*$", "%1")
    if input == "ping" then
        local ts = time()
        local payload = "[[ARCANE_REQUEST]] {\"query\": \"ping\", \"timestamp\": " .. ts .. "}"

        local frame = CreateFrame("Frame", "ArcaneEngineFrame", UIParent, "BasicFrameTemplateWithInset")
        frame:SetSize(450, 150)
        frame:SetPoint("CENTER", 0, 0)
        frame.TitleText:SetText("ArcaneEngine Request")

        local editBox = CreateFrame("EditBox", "ArcaneEngineEditBox", frame, "InputBoxTemplate")
        editBox:SetSize(400, 20)
        editBox:SetPoint("TOP", frame, "TOP", 0, -30)
        editBox:SetAutoFocus(true)
        editBox:SetText(payload)
        editBox:HighlightText()
        editBox:SetFocus()



        local closeButton = CreateFrame("Button", "ArcaneEngineCloseButton", frame, "UIPanelButtonTemplate")
        closeButton:SetSize(80, 22)
        closeButton:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", -10, 10)
        closeButton:SetText("Close")
        closeButton:SetScript("OnClick", function() frame:Hide() end)

        frame:Show()

        DEFAULT_CHAT_FRAME:AddMessage("|cFF00FF00[ArcaneEngine]|r Frame shown with JSON. Ctrl+C to copy.")
    else
        print("[ArcaneEngine] Usage: /arcane ping")
    end
end

SLASH_ARCANE1 = "/arcane"
SlashCmdList["ARCANE"] = HandleArcane

Frame:RegisterEvent("ADDON_LOADED")
Frame:SetScript("OnEvent", function(self, event, ...)
    if event == "ADDON_LOADED" and ... == ADDON_NAME then
        Print("Loaded. Use /arcane ping")
    end
end)
