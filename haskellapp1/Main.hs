-- haskellapp1 — 推箱子终端版（教学）
module Main where

import Control.Exception (IOException, catch)
import Game
import System.IO (hFlush, stdout)

level :: [String]
level =
  [ "#######"
  , "#. . .#"
  , "# $$$ #"
  , "#.$@$.#"
  , "# $$$ #"
  , "#. . .#"
  , "#######"
  ]

toLower :: Char -> Char
toLower c
  | c >= 'A' && c <= 'Z' = toEnum (fromEnum c + 32)
  | otherwise = c

loop :: GameState -> IO ()
loop state = do
  putStrLn ""
  putStr (renderAscii state)
  putStr $ "moves=" ++ show (moves state) ++ (if won state then " WIN!" else "") ++ "\n> "
  hFlush stdout
  mline <- (Just <$> getLine) `catch` (\(_ :: IOException) -> pure Nothing)
  case mline of
    Nothing -> pure ()
    Just line ->
      case dropWhile (== ' ') line of
        [] -> loop state
        (c:_) ->
          let ch = toLower c
              state' = case ch of
                'w' -> tryMove 0 (-1) state
                's' -> tryMove 0 1 state
                'a' -> tryMove (-1) 0 state
                'd' -> tryMove 1 0 state
                'z' -> undo state
                'r' -> fromRows level 0
                _   -> state
          in if ch == 'q'
               then pure ()
               else do
                 if won state' then putStrLn "Level clear!" else pure ()
                 loop state'

main :: IO ()
main = do
  putStrLn "sokoban_haskell — wasd 移动, z 撤销, r 重置, q 退出"
  loop (fromRows level 0)
