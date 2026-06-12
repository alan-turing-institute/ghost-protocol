using UnityEngine;

public class CameraPositionOverlay : MonoBehaviour
{
    [Header("Target")]
    [Tooltip("Camera transform to read. Uses this GameObject if left empty.")]
    public Transform target;

    [Header("Display")]
    public bool showRotation;
    [Min(0)]
    public int decimalPlaces = 3;
    public Vector2 screenOffset = new Vector2(0f, 12f);
    public int fontSize = 18;
    public Color textColor = Color.white;
    public Color backgroundColor = new Color(0f, 0f, 0f, 0.55f);

    private GUIStyle _labelStyle;
    private GUIStyle _boxStyle;
    private Texture2D _backgroundTexture;
    private Color _appliedBackgroundColor;

    private void Awake()
    {
        if (target == null)
        {
            target = transform;
        }
    }

    private void OnGUI()
    {
        if (target == null)
        {
            return;
        }

        EnsureStyles();

        Vector3 position = target.position;
        string format = "F" + decimalPlaces;
        string label = "Camera: "
            + $"x {position.x.ToString(format)}  "
            + $"y {position.y.ToString(format)}  "
            + $"z {position.z.ToString(format)}";

        if (showRotation)
        {
            Vector3 rotation = target.rotation.eulerAngles;
            label += "    Rot: "
                + $"x {rotation.x.ToString(format)}  "
                + $"y {rotation.y.ToString(format)}  "
                + $"z {rotation.z.ToString(format)}";
        }

        Vector2 textSize = _labelStyle.CalcSize(new GUIContent(label));
        const float paddingX = 14f;
        const float paddingY = 8f;
        float width = textSize.x + paddingX * 2f;
        float height = textSize.y + paddingY * 2f;
        Rect rect = new Rect(
            (Screen.width - width) * 0.5f + screenOffset.x,
            screenOffset.y,
            width,
            height);

        GUI.Box(rect, GUIContent.none, _boxStyle);
        GUI.Label(
            new Rect(rect.x + paddingX, rect.y + paddingY, textSize.x, textSize.y),
            label,
            _labelStyle);
    }

    private void OnDestroy()
    {
        if (_backgroundTexture != null)
        {
            Destroy(_backgroundTexture);
        }
    }

    private void EnsureStyles()
    {
        if (_labelStyle == null)
        {
            _labelStyle = new GUIStyle(GUI.skin.label)
            {
                alignment = TextAnchor.MiddleCenter,
                fontStyle = FontStyle.Bold
            };
        }

        if (_boxStyle == null)
        {
            _boxStyle = new GUIStyle(GUI.skin.box);
        }

        _labelStyle.fontSize = fontSize;
        _labelStyle.normal.textColor = textColor;

        if (_backgroundTexture == null || _appliedBackgroundColor != backgroundColor)
        {
            if (_backgroundTexture != null)
            {
                Destroy(_backgroundTexture);
            }

            _backgroundTexture = MakeTexture(backgroundColor);
            _appliedBackgroundColor = backgroundColor;
        }

        _boxStyle.normal.background = _backgroundTexture;
    }

    private Texture2D MakeTexture(Color color)
    {
        Texture2D texture = new Texture2D(1, 1);
        texture.SetPixel(0, 0, color);
        texture.Apply();
        return texture;
    }
}
