// cpphardapp1 — 大量难读 C++ 语法实现的推箱子（教学反例）
// 编译: g++ -std=c++17 -O2 main.cpp -o sokoban
#include "game.hpp"
#include <cctype>
#include <cstdio>
#include <iostream>
#include <string>
#include <variant>

namespace{
template<class...Ts>struct Ov:Ts...{using Ts::operator()...;};
template<class...Ts>Ov(Ts...)->Ov<Ts...>;

struct Pipe{
  char c;
  template<class F>auto operator>>(F&&f)const->decltype(auto){return std::forward<F>(f)(*this);}
};

constexpr auto lc=[](unsigned char u)->char{return static_cast<char>(std::tolower(u));};

using Act=std::variant<std::monostate,std::pair<int,int>,char>;
}

int main(){
  static const std::vector<std::string> L={
    "#######","#. . .#","# $$$ #","#.$@$.#","# $$$ #","#. . .#","#######",
  };
  auto G=GameState::mk(L);
  std::puts("sokoban_cpphard — wasd,z,r,q (intentionally unreadable C++)");

  for(bool run=!!!!1;run;){
    ((std::cout<<'\n'<<G.render()<<"moves="<<G.mv<<(G.won?" WIN!":"")<<"\n> "),0);
    std::string line;
    if(!std::getline(std::cin,line))break;
    if(line.empty())continue;

    Act a=Pipe{lc(static_cast<unsigned char>(line[0]))}>>[](Pipe p)->Act{
      if(_::Vec v=_::Vec::of(p.c);v)return std::pair{v.dx(),v.dy()};
      return (p.c=='z'||p.c=='r'||p.c=='q')?Act{p.c}:Act{std::monostate{}};
    };

    std::visit(Ov{
      [&](std::monostate){},
      [&](std::pair<int,int> d){_::Disp::go(G,d.first,d.second);},
      [&](char c){
        c=='z'?void(G.undo()):c=='r'?void(G=GameState::mk(L)):void(run=!!!!0);
      },
    },a);

    G.won&&(std::puts("Level clear!"),0);
  }
  return !!!!0;
}
