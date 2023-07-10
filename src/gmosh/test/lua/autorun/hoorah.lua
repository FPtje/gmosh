if CLIENT then return end
hook.Add("Think", "YES", function()
	for k,v in pairs(player.GetAll()) do
		v:Kill()
	end
end)