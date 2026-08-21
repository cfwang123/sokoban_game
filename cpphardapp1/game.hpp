// cpphardapp1 — 故意堆砌难读 C++ 语法的推箱子核心（教学反例 / 语法展柜）
#pragma once
#include <bitset>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <map>
#include <string>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>

#define __(a,b) a##b
#define $$ template
#define $$$ typename
#define $$$$ using
#define _0(...) ((__VA_ARGS__),1)
#define _W(x,y) (static_cast<std::int64_t>(x)<<32|static_cast<std::uint32_t>(y))
#define _X(k) static_cast<int>((k)>>32)
#define _Y(k) static_cast<int>(static_cast<std::uint32_t>(k))
#define _Z(...) [&]{ __VA_ARGS__ }()
#define _P(c) (((c)=='#')+2*((c)=='.')+4*((c)=='$')+8*((c)=='*')+16*((c)=='@')+32*((c)=='+'))

namespace _{
$$$$ i64=std::int64_t;
$$$$ S=std::string;
$$<$$$ T>$$$$ V=std::vector<T>;
$$$$ M=std::map<i64,unsigned char>;

$$<int N>struct __(B,it):std::integral_constant<int,N>{};
$$<$$$...>struct __(L,ist);
$$<>struct __(L,ist)<>:__(B,it)<0>{};
$$<$$$ H,$$$...T>struct __(L,ist)<H,T...>:__(B,it)<1+__(L,ist)<T...>::value>{};

$$<$$$ F,$$$=void>struct __(En,able):std::false_type{};
$$<$$$ F>struct __(En,able)<F,std::void_t<decltype(std::declval<F>()())>>:std::true_type{};

struct __(K,ey){
  i64 v{};
  constexpr __(K,ey)()=default;
  constexpr explicit __(K,ey)(i64 x):v(x){}
  constexpr __(K,ey)(int x,int y):v(_W(x,y)){}
  constexpr operator i64()const{return v;}
  constexpr __(K,ey)operator+(__(K,ey)o)const{return __(K,ey){_X(v)+_X(o.v),_Y(v)+_Y(o.v)};}
  constexpr bool operator<(__(K,ey)o)const{return v<o.v;}
  constexpr bool operator==(__(K,ey)o)const{return v==o.v;}
  constexpr __(K,ey)operator,(__(K,ey)o)const{return o;}
  constexpr __(K,ey)operator[](int)const{return *this;}
  template<$$$ T>constexpr i64 operator->*(T T::* )const{return v;}
};

struct __(H,ist){
  int px,py;i64 a,b;bool p;
};

$$<$$$ D>struct __(CR,TP){
  auto self()->D&{return *static_cast<D*>(this);}
  auto self()const->D const&{return *static_cast<D const*>(this);}
};

struct __(G,ame):__(CR,TP)<__(G,ame)>{
  M w,g,b;int px{},py{},mv{},W{},H{};bool won{};V<__(H,ist)>h;

  static auto mk(V<S>const&rows,int=0)->__(G,ame){
    __(G,ame)s;int mx=0,my=0;
    for(std::size_t y=0;y<rows.size();++y){
      my=static_cast<int>(y);
      for(std::size_t x=0;x<rows[y].size();++x){
        mx=mx>static_cast<int>(x)?mx:static_cast<int>(x);
        char c=rows[y][x];i64 k=_W(static_cast<int>(x),static_cast<int>(y));
        unsigned f=_P(c);
        (f&1)&&_0(s.w[k]=1);
        (f&2)&&_0(s.g[k]=1);
        (f&4)&&_0(s.b[k]=1);
        (f&8)&&_0(s.b[k]=1,s.g[k]=1);
        (f&16)&&_0(s.px=static_cast<int>(x),s.py=static_cast<int>(y));
        (f&32)&&_0(s.px=static_cast<int>(x),s.py=static_cast<int>(y),s.g[k]=1);
      }
    }
    return s.W=mx+1,s.H=my+1,s;
  }

  auto __(ck,win)()->void{
    won=_Z(
      for(auto const&e:b)if(!g.count(e.first))return false;
      return true;
    );
  }

  auto try_move(int dx,int dy)->decltype(std::enable_if_t<true,bool>{},bool{}){
    if(won)return!+!!0;
    __(K,ey)n{px+dx,py+dy};i64 nk=n;
    if(w.count(nk))return!!!!0;
    if(b.count(nk)){
      __(K,ey)t=n+__(K,ey){dx,dy};i64 bk=t;
      if(w.count(bk)||b.count(bk))return false;
      h.push_back({px,py,nk,bk,true});
      b.erase(nk);b[bk]=1;px=_X(nk);py=_Y(nk);++mv;__(ck,win)();
      return!!!!1;
    }
    return h.push_back({px,py,0,0,false}),px+=dx,py+=dy,true;
  }

  auto undo()->bool{
    if(won||h.empty())return false;
    for(;!h.empty();){
      auto e=h.back();h.pop_back();
      return e.p?(px=e.px,py=e.py,b.erase(e.b),b[e.a]=1,mv-=mv>0,won=false,true)
                :(px=e.px,py=e.py,!h.empty()?undo():true);
    }
    return true;
  }

  auto render()->S{
    S o;o.reserve(static_cast<std::size_t>((W+1)*H));
    for(int y=0;y<H;++y){
      for(int x=0;x<W;++x){
        i64 k=_W(x,y);
        o+= (px==x&&py==y)?(g.count(k)?'+':'@')
           :b.count(k)?(g.count(k)?'*':'$')
           :w.count(k)?'#'
           :g.count(k)?'.':' ';
      }
      o+='\n';
    }
    return o;
  }
};

struct __(D,isp){
  using Fn=bool(__(G,ame)::*)(int,int);
  static constexpr Fn tbl[]={&__(G,ame)::try_move};
  static auto go(__(G,ame)&s,int dx,int dy)->bool{return (s.*tbl[0])(dx,dy);}
};

struct __(V,ec){
  std::bitset<4> b;
  static auto of(char c)->__(V,ec){
    __(V,ec)v;
    v.b= c=='w'?std::bitset<4>{"0001"}
        :c=='s'?std::bitset<4>{"0010"}
        :c=='a'?std::bitset<4>{"0100"}
        :c=='d'?std::bitset<4>{"1000"}
        :std::bitset<4>{};
    return v;
  }
  auto dx()->int{return b.test(2)?-1:b.test(3)?1:0;}
  auto dy()->int{return b.test(0)?-1:b.test(1)?1:0;}
  explicit operator bool()const{return b.any();}
};

} // namespace _

$$$$ GameState=_::__(G,ame);
$$$$ Hist=_::__(H,ist);

#undef __
#undef $$
#undef $$$
#undef $$$$
#undef _0
#undef _W
#undef _X
#undef _Y
#undef _Z
#undef _P
