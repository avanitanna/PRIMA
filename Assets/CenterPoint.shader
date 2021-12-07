Shader "Center"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}
    }
    SubShader
    {
        Cull Off ZWrite Off ZTest Always
        CGINCLUDE
        #include "UnityCG.cginc"
        #pragma fragmentoption ARB_precision_hint_fastest
        #pragma enable_d3d11_debug_symbols
        
        struct appdata
        {
            float4 vertex : POSITION;
            float2 uv : TEXCOORD0;
        };
                    
        struct v2f
        {
            float4 grabPos : TEXCOORD0;
            float4 pos : SV_POSITION;
        };
        
        v2f vert (appdata v)
        {
            v2f o;
            o.pos = UnityObjectToClipPos(v.vertex);
            o.grabPos = ComputeGrabScreenPos(o.pos);
            return o;
        }
        
        ENDCG

        GrabPass {
            "_MainTex"
        }
       Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma enable_d3d11_debug_symbols

            sampler2D _MainTex;
            float4 _MainTex_TexelSize;

            uniform RWStructuredBuffer<double> debugBuffer : register(u2);
            
            float scotomaSize; 
            float gazeY;
            float gazeX;
            float aspectRatio; 
            
            fixed4 frag (v2f i) : SV_Target
            {
                sampler2D tex = _MainTex; 
                float _texelw = _MainTex_TexelSize.x;
                float2 uv = i.grabPos;
                uint sampleDistance = 15; 

                float distY = (uv.y-gazeY); 
                float distX = (uv.x-gazeX) / aspectRatio ; 
                if( sqrt( distY*distY + distX*distX  ) < scotomaSize)
                {
                    return float4(1,0,1,1);
                }
                
                return tex2D(tex, uv); 
            }
            ENDCG
        }
    }
}