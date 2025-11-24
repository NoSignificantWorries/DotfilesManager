local function main()
	local script_path = debug.getinfo(1).source:match("@?(.*/)")
	script_path = script_path or "./"
	print(script_path)

	local config_path = script_path .. "../example/packages/base.lua"
	local stages = dofile(config_path)

	if not stages then
		error("Failed to load configuration from: " .. config_path)
	end

	print("Loaded packages:")
	for name, content in pairs(stages or {}) do
		print(name)
	end

	return true
end

ok, err = pcall(main)
if not ok then
	print("Error:", err)
	os.exit(1)
else
	print("Completed succesfully")
end
