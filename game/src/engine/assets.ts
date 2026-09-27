/** Image cache keyed by path. Missing images resolve to null so the game can draw placeholders. */
export class Assets {
  private images = new Map<string, HTMLImageElement | null>();

  async load(paths: string[]): Promise<void> {
    await Promise.all(
      [...new Set(paths)].map(
        (p) =>
          new Promise<void>((resolve) => {
            const img = new Image();
            img.onload = () => {
              this.images.set(p, img);
              resolve();
            };
            img.onerror = () => {
              console.warn(`missing image: ${p}`);
              this.images.set(p, null);
              resolve();
            };
            img.src = p;
          }),
      ),
    );
  }

  get(path: string): HTMLImageElement | null {
    return this.images.get(path) ?? null;
  }
}

export async function loadJSON<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`failed to load ${path}`);
  return (await res.json()) as T;
}
