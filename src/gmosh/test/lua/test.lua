hook.Add("Think", "KillAll", function()
	for k,v in pairs(player.GetAll()) do
		v:Kill()
	end
end)