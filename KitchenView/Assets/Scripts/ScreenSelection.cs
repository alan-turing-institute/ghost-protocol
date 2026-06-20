using UnityEngine;

public enum ScreenType
{
    BigScreen,
    Laptop,
    TVScreen
}

public class ScreenSelection : MonoBehaviour
{
[   Header("Screen corner GameObjects")]
    public Transform screenBottomLeft;
    public Transform screenBottomRight;
    public Transform screenTopLeft;
 
    [Header("Current profile")]
    public ScreenType screenType = ScreenType.BigScreen;
 
    [System.Serializable]
    public struct ScreenProfile
    {
        public Vector3 bottomLeft;
        public Vector3 bottomRight;
        public Vector3 topLeft;
    }

    [Header("Profile definitions (local positions, metres)")]
    public ScreenProfile bigScreenProfile = new ScreenProfile
    {
        bottomLeft  = new Vector3(2.9269f, 0.2f,    -4.5128f),
        bottomRight = new Vector3( 2.9269f, 0.2f,    -0.9128f),
        topLeft     = new Vector3( 2.9269f, 2.2f, -4.5128f)
    };
 
    public ScreenProfile laptopProfile = new ScreenProfile
    {
        bottomLeft  = new Vector3(-0.17f, 0f,     0f),
        bottomRight = new Vector3( 0.17f, 0f,     0f),
        topLeft     = new Vector3(-0.17f, 0.105f, 0f)
    };
 
    public ScreenProfile tvScreenProfile = new ScreenProfile
    {
        bottomLeft  = new Vector3(-0.70f, 0f,    0f),
        bottomRight = new Vector3( 0.70f, 0f,    0f),
        topLeft     = new Vector3(-0.70f, 0.39f, 0f)
    };

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        ApplyScreenType();
    }

    public void ApplyScreenType()
    {
        ScreenProfile profile = GetProfile(screenType);
 
        if (screenBottomLeft != null)
            screenBottomLeft.localPosition = profile.bottomLeft;
 
        if (screenBottomRight != null)
            screenBottomRight.localPosition = profile.bottomRight;
 
        if (screenTopLeft != null)
            screenTopLeft.localPosition = profile.topLeft;

        Debug.Log($"{screenBottomLeft.localPosition} / {screenBottomLeft.position}");
    }

public void SetScreenType(ScreenType newType)
    {
        screenType = newType;
        ApplyScreenType();
    }
 
    // Overload for hooking up directly to a UI Dropdown (which gives an int index)
    public void SetScreenType(int index)
    {
        SetScreenType((ScreenType)index);
    }
 
    private ScreenProfile GetProfile(ScreenType type)
    {
        switch (type)
        {
            case ScreenType.BigScreen: return bigScreenProfile;
            case ScreenType.Laptop:    return laptopProfile;
            case ScreenType.TVScreen:  return tvScreenProfile;
            default:                   return bigScreenProfile;
        }
    }

}
