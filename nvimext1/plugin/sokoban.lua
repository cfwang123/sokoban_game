-- 命令 :Sokoban
vim.api.nvim_create_user_command("Sokoban", function()
  require("sokoban").open()
end, { desc = "Play Sokoban (teaching demo)" })
