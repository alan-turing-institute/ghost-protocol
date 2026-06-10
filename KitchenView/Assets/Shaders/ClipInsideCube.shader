Shader "Custom/Clip Inside Cube"
{
    Properties
    {
        _Color ("Color", Color) = (1,1,1,1)
    }

    SubShader
    {
        Tags { "RenderType"="Opaque" }

        Pass
        {
            CGPROGRAM

            #pragma vertex vert
            #pragma fragment frag

            #include "UnityCG.cginc"

            fixed4 _Color;
            float4x4 _CubeWorldToLocal;

            struct appdata
            {
                float4 vertex : POSITION;
            };

            struct v2f
            {
                float4 pos : SV_POSITION;
                float3 worldPos : TEXCOORD0;
            };

            v2f vert(appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.worldPos = mul(unity_ObjectToWorld, v.vertex).xyz;
                return o;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                float3 cubeLocalPos = mul(_CubeWorldToLocal, float4(i.worldPos, 1)).xyz;

                // Unity's default cube spans -0.5 to +0.5 in local space.
                // If the point is inside that cube, discard it.
                if (
                    abs(cubeLocalPos.x) < 0.5 &&
                    abs(cubeLocalPos.y) < 0.5 &&
                    abs(cubeLocalPos.z) < 0.5
                )
                {
                    discard;
                }

                return _Color;
            }

            ENDCG
        }
    }
}