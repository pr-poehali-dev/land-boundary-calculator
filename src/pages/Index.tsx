import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';
import { useToast } from '@/hooks/use-toast';

interface PlotData {
  cadastralNumber: string;
  address: string;
  area: number;
  category: string;
  costPerPoint: number;
  pointsCount: number;
  totalCost: number;
  coordinates: [number, number][];
}

const Index = () => {
  const [cadastralNumber, setCadastralNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [plotData, setPlotData] = useState<PlotData | null>(null);
  const { toast } = useToast();

  const validateCadastralNumber = (value: string): boolean => {
    const pattern = /^\d{2}:\d{2}:\d{6,7}:\d+$/;
    return pattern.test(value);
  };

  const calculateCost = (area: number): { costPerPoint: number; pointsCount: number; totalCost: number } => {
    const pointsCount = Math.ceil(area / 200) + 4;
    const costPerPoint = area > 10000 ? 3500 : area > 5000 ? 4000 : 4500;
    const totalCost = pointsCount * costPerPoint;
    return { costPerPoint, pointsCount, totalCost };
  };

  const handleSearch = async () => {
    if (!validateCadastralNumber(cadastralNumber)) {
      toast({
        title: 'Ошибка валидации',
        description: 'Введите корректный кадастровый номер (например: 77:09:0005004:1234)',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);

    setTimeout(() => {
      const mockArea = Math.floor(Math.random() * 15000) + 500;
      const costs = calculateCost(mockArea);
      
      const mockData: PlotData = {
        cadastralNumber,
        address: 'Московская область, Раменский район, д. Заболотье',
        area: mockArea,
        category: 'Земли населённых пунктов',
        ...costs,
        coordinates: [
          [55.7558, 37.6173],
          [55.7558, 37.6193],
          [55.7548, 37.6193],
          [55.7548, 37.6173],
        ],
      };

      setPlotData(mockData);
      setLoading(false);
      
      toast({
        title: 'Данные получены',
        description: 'Информация о участке успешно загружена',
      });
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="text-center mb-12 animate-fade-in">
          <div className="inline-block p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl mb-4">
            <Icon name="MapPin" size={40} className="text-white" />
          </div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent mb-4">
            Калькулятор выноса границ
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Рассчитайте стоимость межевания по кадастровому номеру участка
          </p>
        </div>

        <Card className="mb-8 border-2 shadow-xl animate-scale-in">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-2xl">
              <Icon name="Search" size={24} className="text-purple-600" />
              Поиск участка
            </CardTitle>
            <CardDescription>
              Введите кадастровый номер в формате XX:XX:XXXXXXX:XXXX
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <div className="flex-1">
                <Input
                  placeholder="77:09:0005004:1234"
                  value={cadastralNumber}
                  onChange={(e) => setCadastralNumber(e.target.value)}
                  className="h-14 text-lg border-2 focus:border-purple-500"
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
              </div>
              <Button
                onClick={handleSearch}
                disabled={loading}
                size="lg"
                className="h-14 px-8 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-lg font-semibold"
              >
                {loading ? (
                  <>
                    <Icon name="Loader2" size={20} className="mr-2 animate-spin" />
                    Поиск...
                  </>
                ) : (
                  <>
                    <Icon name="Search" size={20} className="mr-2" />
                    Найти
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {plotData && (
          <div className="grid md:grid-cols-2 gap-6 animate-slide-up">
            <Card className="border-2 shadow-xl hover:shadow-2xl transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-xl">
                  <Icon name="FileText" size={22} className="text-blue-600" />
                  Информация об участке
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                  <span className="text-gray-600 font-medium">Кадастровый номер:</span>
                  <Badge variant="secondary" className="text-base px-3 py-1">
                    {plotData.cadastralNumber}
                  </Badge>
                </div>
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                  <span className="text-gray-600 font-medium">Площадь:</span>
                  <span className="font-bold text-lg text-blue-600">
                    {plotData.area.toLocaleString()} м²
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-pink-50 rounded-lg">
                  <span className="text-gray-600 font-medium">Категория:</span>
                  <span className="font-semibold text-pink-600">{plotData.category}</span>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-600 font-medium flex items-center gap-2 mb-2">
                    <Icon name="MapPin" size={18} />
                    Адрес:
                  </span>
                  <span className="text-gray-800">{plotData.address}</span>
                </div>
              </CardContent>
            </Card>

            <Card className="border-2 shadow-xl hover:shadow-2xl transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-xl">
                  <Icon name="Calculator" size={22} className="text-green-600" />
                  Расчет стоимости
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <span className="text-gray-600 font-medium">Количество точек:</span>
                  <span className="font-bold text-lg text-green-600">{plotData.pointsCount}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-orange-50 rounded-lg">
                  <span className="text-gray-600 font-medium">Стоимость за точку:</span>
                  <span className="font-bold text-lg text-orange-600">
                    {plotData.costPerPoint.toLocaleString()} ₽
                  </span>
                </div>
                <div className="p-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl text-white">
                  <div className="flex justify-between items-center">
                    <span className="text-lg font-medium">Итоговая стоимость:</span>
                    <span className="text-3xl font-bold">
                      {plotData.totalCost.toLocaleString()} ₽
                    </span>
                  </div>
                </div>
                <div className="flex items-start gap-2 p-3 bg-blue-50 rounded-lg">
                  <Icon name="Info" size={18} className="text-blue-600 mt-1" />
                  <p className="text-sm text-gray-600">
                    Расчет является предварительным. Точная стоимость определяется после осмотра участка специалистом.
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card className="md:col-span-2 border-2 shadow-xl">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-xl">
                  <Icon name="Map" size={22} className="text-purple-600" />
                  Визуализация участка
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="relative bg-gradient-to-br from-blue-100 to-green-100 rounded-xl p-8 h-96 flex items-center justify-center overflow-hidden">
                  <div className="absolute inset-0 opacity-10">
                    <div className="grid grid-cols-12 gap-2 h-full">
                      {Array.from({ length: 144 }).map((_, i) => (
                        <div key={i} className="border border-gray-400" />
                      ))}
                    </div>
                  </div>
                  <div className="relative z-10 text-center">
                    <div className="inline-block p-6 bg-white rounded-2xl shadow-2xl border-4 border-purple-500 mb-4">
                      <Icon name="MapPin" size={48} className="text-purple-600" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-800 mb-2">
                      Участок {plotData.cadastralNumber}
                    </h3>
                    <p className="text-gray-600 mb-4">
                      Площадь: {plotData.area.toLocaleString()} м²
                    </p>
                    <div className="flex justify-center gap-4">
                      {plotData.coordinates.map((coord, idx) => (
                        <Badge key={idx} variant="outline" className="bg-white">
                          Точка {idx + 1}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="mt-4 p-4 bg-yellow-50 rounded-lg flex items-start gap-3">
                  <Icon name="AlertCircle" size={20} className="text-yellow-600 mt-0.5" />
                  <p className="text-sm text-gray-700">
                    Для интеграции с API NSPD и отображения реальных данных кадастра, требуется подключение к официальному API Росреестра.
                    Сейчас отображаются демонстрационные данные.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {!plotData && (
          <Card className="border-2 border-dashed shadow-lg animate-fade-in">
            <CardContent className="py-16">
              <div className="text-center text-gray-400">
                <Icon name="Search" size={64} className="mx-auto mb-4 opacity-50" />
                <p className="text-xl">Введите кадастровый номер для начала расчета</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default Index;
